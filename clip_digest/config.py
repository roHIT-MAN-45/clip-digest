from pathlib import Path
from dataclasses import dataclass

from .errors import ConfigError

MIN_QUALITY = 1
MAX_QUALITY = 100
MIN_COMPRESSION = 0
MAX_COMPRESSION = 6
VALID_FORMATS = ("webp", "png", "jpg")


# holds every configurable processing setting with balanced defaults
@dataclass(frozen=True)
class Config:
    should_transcribe: bool = True
    should_time_words: bool = True
    should_extract_frames: bool = True
    should_write_manifest: bool = True
    quality: int = 85
    frame_rate: float = 1.0
    image_format: str = "webp"
    compression_level: int = 6
    frame_pattern: str = "frame_%04d"
    language: str | None = None
    start_time: float | None = None
    end_time: float | None = None
    output_root: Path = Path("output")

    # validates every field against its documented range
    def __post_init__(self) -> None:
        if self.frame_rate <= 0:
            raise ConfigError(f"frame_rate must be positive, got {self.frame_rate}")

        if not MIN_QUALITY <= self.quality <= MAX_QUALITY:
            raise ConfigError(f"quality must be {MIN_QUALITY} to {MAX_QUALITY}, got {self.quality}")

        if not MIN_COMPRESSION <= self.compression_level <= MAX_COMPRESSION:
            raise ConfigError(
                f"compression_level must be {MIN_COMPRESSION} to {MAX_COMPRESSION}, "
                f"got {self.compression_level}"
            )

        if self.image_format not in VALID_FORMATS:
            raise ConfigError(f"image_format must be one of {VALID_FORMATS}, got '{self.image_format}'")

        self._validate_time_range()

    # ensures the start and end bounds form a valid window
    def _validate_time_range(self) -> None:
        if self.start_time is not None and self.start_time < 0:
            raise ConfigError(f"start_time must not be negative, got {self.start_time}")

        if self.end_time is not None and self.end_time < 0:
            raise ConfigError(f"end_time must not be negative, got {self.end_time}")

        has_both = self.start_time is not None and self.end_time is not None

        if has_both and self.start_time >= self.end_time:
            raise ConfigError(f"start_time {self.start_time} must be below end_time {self.end_time}")

    # builds a config from a plain dict, rejecting unknown keys early
    @classmethod
    def from_dict(cls, values: dict) -> "Config":
        allowed = {field for field in cls.__dataclass_fields__}
        unknown = set(values) - allowed

        if unknown:
            raise ConfigError(f"unknown config keys {sorted(unknown)}, allowed {sorted(allowed)}")

        prepared = dict(values)

        if "output_root" in prepared:
            prepared["output_root"] = Path(prepared["output_root"])

        return cls(**prepared)
