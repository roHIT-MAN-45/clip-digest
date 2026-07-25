import logging
from pathlib import Path
from dataclasses import field, dataclass

from .config import Config
from .frames import extract_frames
from .transcript import Segment, extract_transcript, has_audio_stream

logger = logging.getLogger(__name__)

FRAMES_DIR_NAME = "frames"
TRANSCRIPT_DIR_NAME = "transcript"


# structured result returned to the caller instead of parsing output
@dataclass(frozen=True)
class Result:
    frame_count: int = 0
    frames_dir: Path | None = None
    transcript_dir: Path | None = None
    segments: list[Segment] = field(default_factory=list)


# runs the enabled stages for one video and returns their combined result
def run(*, video_path: str | Path, config: Config | None = None) -> Result:
    video_path = Path(video_path)
    config = config or Config()
    output_dir = Path(config.output_root) / video_path.stem
    frame_count = 0
    frames_dir = None
    segments: list[Segment] = []
    transcript_dir = None

    if config.should_extract_frames:
        frames_dir = output_dir / FRAMES_DIR_NAME
        logger.info("extracting frames.", extra={"video": video_path.name})
        frame_count = extract_frames(video_path=video_path, output_dir=frames_dir, config=config)

    if config.should_transcribe and has_audio_stream(video_path=video_path):
        transcript_dir = output_dir / TRANSCRIPT_DIR_NAME
        logger.info("transcribing audio.", extra={"video": video_path.name})
        segments = extract_transcript(video_path=video_path, output_dir=transcript_dir, config=config)
    elif config.should_transcribe:
        logger.info("no audio track found.", extra={"video": video_path.name})

    return Result(
        frame_count=frame_count,
        frames_dir=frames_dir,
        segments=segments,
        transcript_dir=transcript_dir,
    )
