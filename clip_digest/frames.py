import json
import logging
import subprocess
from pathlib import Path

from .config import Config
from .errors import ExtractionError, VideoNotFoundError, MissingDependencyError
from .time_format import format_timestamp

logger = logging.getLogger(__name__)

MANIFEST_NAME = "manifest.json"
FORMAT_CODECS = {"webp": "libwebp", "png": "png", "jpg": "mjpeg"}
QUALITY_FORMATS = ("webp", "jpg")
COMPRESSION_FORMATS = ("webp", "png")


# confirms ffmpeg is callable before extraction begins
def check_ffmpeg() -> None:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except FileNotFoundError:
        raise MissingDependencyError("ffmpeg is not installed or not on PATH")


# builds the codec and quality flags for the configured image format
def build_encode_args(config: Config) -> list[str]:
    args = ["-c:v", FORMAT_CODECS[config.image_format]]

    if config.image_format in QUALITY_FORMATS:
        args += ["-quality", str(config.quality)]

    if config.image_format in COMPRESSION_FORMATS:
        args += ["-compression_level", str(config.compression_level)]

    return args


# assembles the full ffmpeg command including the trim window
def build_command(*, video_path: Path, output_dir: Path, config: Config) -> list[str]:
    command = ["ffmpeg"]

    # seeking before the input makes the trim fast and frame accurate
    if config.start_time is not None:
        command += ["-ss", str(config.start_time)]

    command += ["-i", str(video_path)]

    if config.end_time is not None:
        duration = config.end_time - (config.start_time or 0)
        command += ["-t", str(duration)]

    pattern = str(output_dir / f"{config.frame_pattern}.{config.image_format}")
    command += ["-vf", f"fps={config.frame_rate}", *build_encode_args(config)]
    command += ["-fps_mode", "vfr", "-hide_banner", "-loglevel", "error", pattern]

    return command


# writes a manifest mapping each frame to its source timestamp
def write_manifest(*, output_dir: Path, frame_count: int, config: Config) -> None:
    interval = 1.0 / config.frame_rate
    offset = config.start_time or 0
    entries = []

    for index in range(frame_count):
        seconds = index * interval + offset
        entries.append(
            {
                "frame": f"{config.frame_pattern % (index + 1)}.{config.image_format}",
                "timestamp_seconds": round(seconds, 3),
                "timestamp_label": format_timestamp(seconds),
            }
        )

    path = output_dir / MANIFEST_NAME
    path.write_text(json.dumps(entries, indent=2), encoding="utf-8")


# extracts frames into output_dir and returns the frame count
def extract_frames(*, video_path: Path, output_dir: Path, config: Config) -> int:
    if not video_path.exists():
        raise VideoNotFoundError(f"video file not found {video_path}")

    check_ffmpeg()
    output_dir.mkdir(parents=True, exist_ok=True)
    command = build_command(video_path=video_path, output_dir=output_dir, config=config)

    try:
        subprocess.run(command, capture_output=True, check=True)
    except subprocess.CalledProcessError as error:
        detail = error.stderr.decode(errors="replace") if error.stderr else ""
        logger.error("frame extraction failed.", extra={"video": str(video_path), "error": detail})

        raise ExtractionError(f"ffmpeg failed for {video_path}") from error

    frames = sorted(output_dir.glob(f"frame_*.{config.image_format}"))
    frame_count = len(frames)

    if config.should_write_manifest:
        write_manifest(output_dir=output_dir, frame_count=frame_count, config=config)

    return frame_count
