from .errors import ConfigError

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600


# parses a SS MM:SS or HH:MM:SS string into total seconds
def parse_time(value: str) -> float:
    parts = value.split(":")

    if len(parts) == 1:
        return float(parts[0])

    if len(parts) == 2:
        minutes, seconds = float(parts[0]), float(parts[1])

        return minutes * SECONDS_PER_MINUTE + seconds

    if len(parts) == 3:
        hours, minutes, seconds = float(parts[0]), float(parts[1]), float(parts[2])

        return hours * SECONDS_PER_HOUR + minutes * SECONDS_PER_MINUTE + seconds

    raise ConfigError(f"invalid time '{value}', use SS, MM:SS, or HH:MM:SS")


# formats a second count as a zero padded HH:MM:SS label
def format_timestamp(seconds: float) -> str:
    hours = int(seconds // SECONDS_PER_HOUR)
    minutes = int((seconds % SECONDS_PER_HOUR) // SECONDS_PER_MINUTE)
    whole = int(seconds % SECONDS_PER_MINUTE)

    return f"{hours:02d}:{minutes:02d}:{whole:02d}"
