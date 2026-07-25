import json
import logging
from pathlib import Path
from dataclasses import asdict, dataclass

from .config import Config
from .errors import ExtractionError, VideoNotFoundError, MissingDependencyError

logger = logging.getLogger(__name__)

TRANSCRIPT_NAME = "transcript.json"

# fixed internal model keeps transcription behaviour identical everywhere
_WHISPER_MODEL = "small"


# one span of transcribed speech with its start and end in seconds
@dataclass(frozen=True)
class Segment:
    start: float
    end: float
    text: str


# loads the fixed whisper model or reports a missing dependency
def load_model():
    try:
        import whisper
    except ImportError:
        raise MissingDependencyError("openai-whisper is not installed, run pip install openai-whisper")

    return whisper.load_model(_WHISPER_MODEL)


# builds whisper clip bounds from the configured trim window
def build_clip_range(config: Config) -> list[float] | str:
    if config.start_time is None and config.end_time is None:
        return "0"

    bounds = [config.start_time or 0]

    if config.end_time is not None:
        bounds.append(config.end_time)

    return bounds


# converts a raw whisper result into precise segment objects
def to_segments(result: dict) -> list[Segment]:
    segments = []

    for raw in result["segments"]:
        words = raw.get("words") or []
        # word bounds are tighter than segment bounds when available
        start = words[0]["start"] if words else raw["start"]
        end = words[-1]["end"] if words else raw["end"]
        segments.append(Segment(start=round(start, 3), end=round(end, 3), text=raw["text"].strip()))

    return segments


# transcribes the video into output_dir and returns the segments
def extract_transcript(*, video_path: Path, output_dir: Path, config: Config) -> list[Segment]:
    if not video_path.exists():
        raise VideoNotFoundError(f"video file not found {video_path}")

    model = load_model()
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = model.transcribe(
            str(video_path),
            language=config.language,
            word_timestamps=config.should_time_words,
            clip_timestamps=build_clip_range(config),
        )
    except Exception as error:
        logger.error("transcription failed.", extra={"video": str(video_path), "error": str(error)})

        raise ExtractionError(f"whisper failed for {video_path}") from error

    segments = to_segments(result)
    path = output_dir / TRANSCRIPT_NAME
    path.write_text(json.dumps([asdict(seg) for seg in segments], indent=2, ensure_ascii=False), encoding="utf-8")

    return segments
