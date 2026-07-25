# clip-digest

Extract frames and an accurate transcript from a single video. Point it at a
video and it writes timestamped image frames and a timestamped transcript. It
is configured through a single object and returns a structured result.

## Requirements

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) available on `PATH` (frame extraction)
- `openai-whisper` (installed as a dependency; transcription)

## Install

```bash
pip install clip-digest
```

Install from a local checkout instead:

```bash
pip install .
```

## Usage

Call `run` with a video path. With no config, balanced defaults apply.

```python
from clip_digest import Config, run

result = run(video_path="meeting.mp4")

print(result.frame_count)      # frames written
print(result.frames_dir)       # output/meeting/frames
print(result.transcript_dir)   # output/meeting/transcript

for segment in result.segments:
    print(segment.start, segment.text)
```

Override only what a use case needs:

```python
result = run(video_path="demo.mp4", config=Config(frame_rate=2.0, image_format="png"))
```

Build a config from a plain dict (unknown keys are rejected):

```python
config = Config.from_dict({"frame_rate": 0.5, "language": "es", "quality": 80})
result = run(video_path="entrevista.mp4", config=config)
```

Branch on typed errors:

```python
from clip_digest import run, VideoNotFoundError, MissingDependencyError, ConfigError

try:
    result = run(video_path=path)
except VideoNotFoundError:
    ...   # pick another file
except MissingDependencyError:
    ...   # report environment problem
except ConfigError:
    ...   # fix parameters and retry
```

## Configuration options

The transcription model is fixed internally and is not configurable, so
transcription behaves identically across every use case. Everything below is
adjustable.

| Option                  | Default        | What it does                           | When to adjust                                      |
| ----------------------- | -------------- | -------------------------------------- | --------------------------------------------------- |
| `frame_rate`            | `1.0`          | Frames sampled per second              | Raise for fast motion, lower for static screencasts |
| `quality`               | `85`           | webp and jpg quality, 1 to 100         | Lower to shrink files, raise for maximum fidelity   |
| `compression_level`     | `6`            | webp and png effort, 0 to 6            | Lower for faster extraction on long videos          |
| `image_format`          | `"webp"`       | Frame format: `webp`, `png`, `jpg`     | Use `png` for lossless frames feeding OCR           |
| `frame_pattern`         | `"frame_%04d"` | printf stem for frame files            | Match an external naming scheme                     |
| `language`              | `None`         | Language code, or auto detect          | Set when the language is known to skip detection    |
| `start_time`            | `None`         | First second to process                | Skip leading footage                                |
| `end_time`              | `None`         | Last second to process                 | Skip trailing footage                               |
| `output_root`           | `"output"`     | Base output directory                  | Redirect results elsewhere                          |
| `should_extract_frames` | `True`         | Extract frames                         | Disable to transcribe only                          |
| `should_transcribe`     | `True`         | Transcribe audio                       | Disable to extract frames only                      |
| `should_write_manifest` | `True`         | Write the frame timestamp manifest     | Disable when only images are needed                 |
| `should_time_words`     | `True`         | Word level timestamps for tight bounds | Disable for faster transcription                    |

## Output layout

```
output/<video_stem>/
├── frames/
│   ├── frame_0001.webp
│   └── manifest.json
└── transcript/
    └── transcript.json
```

## Command line

A thin CLI is provided for manual use:

```bash
clip-digest meeting.mp4 --frame-rate 2 --image-format png
clip-digest meeting.mp4 --only-transcript --language en
```
