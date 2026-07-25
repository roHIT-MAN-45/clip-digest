import sys
import logging
import argparse

from .config import Config
from .pipeline import run
from .errors import VideoDigestError
from .time_format import parse_time


# defines the command line arguments mirroring the config fields
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract frames and a transcript from a single video.")
    parser.add_argument("video_path", help="path to the video file")
    parser.add_argument("--output-root", default="output", help="base output directory")
    parser.add_argument("--frame-rate", type=float, default=1.0, help="frames sampled per second")
    parser.add_argument("--quality", type=int, default=85, help="webp and jpg quality from 1 to 100")
    parser.add_argument("--image-format", default="webp", choices=("webp", "png", "jpg"))
    parser.add_argument("--language", default=None, help="language code or omit to auto detect")
    parser.add_argument("--start-time", type=parse_time, default=None, help="trim start as SS MM:SS or HH:MM:SS")
    parser.add_argument("--end-time", type=parse_time, default=None, help="trim end as SS MM:SS or HH:MM:SS")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--only-frames", action="store_true", help="extract frames only")
    group.add_argument("--only-transcript", action="store_true", help="transcribe only")

    return parser


# maps parsed arguments onto a validated config object
def build_config(args: argparse.Namespace) -> Config:
    return Config(
        quality=args.quality,
        frame_rate=args.frame_rate,
        image_format=args.image_format,
        language=args.language,
        start_time=args.start_time,
        end_time=args.end_time,
        output_root=args.output_root,
        should_extract_frames=not args.only_transcript,
        should_transcribe=not args.only_frames,
    )


# parses arguments, runs the pipeline, and reports the outcome
def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = build_parser().parse_args()

    try:
        result = run(video_path=args.video_path, config=build_config(args))
    except VideoDigestError as error:
        print(f"error {error}", file=sys.stderr)
        sys.exit(1)

    print(f"frames extracted {result.frame_count}")
    print(f"transcript segments {len(result.segments)}")


if __name__ == "__main__":
    main()
