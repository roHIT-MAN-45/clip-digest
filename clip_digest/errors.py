# base class for every error this package raises
class VideoDigestError(Exception):
    pass


# raised when a configuration value falls outside its documented range
class ConfigError(VideoDigestError):
    pass


# raised when the input video path does not exist
class VideoNotFoundError(VideoDigestError):
    pass


# raised when ffmpeg or whisper is missing from the environment
class MissingDependencyError(VideoDigestError):
    pass


# raised when frame extraction or transcription fails at runtime
class ExtractionError(VideoDigestError):
    pass
