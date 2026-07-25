# clip-digest

> Extract timestamped frames and a transcript from a single video

---

## ❶ Requirements

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) on `PATH` — frame extraction
- `openai-whisper` — installed as a dependency, handles transcription

---

## ❷ Installation

Install from PyPI:

```bash
pip install clip-digest
```

Install from a local checkout:

```bash
pip install .
```

---

## ❸ Usage

Call `run` with a video path — balanced defaults apply when no config is passed:

```python
from clip_digest import Config, run

result = run(video_path="meeting.mp4")

print(result.frame_count)      # frames written
print(result.frames_dir)       # output/meeting/frames
print(result.transcript_dir)   # output/meeting/transcript

for segment in result.segments:
    print(segment.start, segment.text)
```

Override only what a case needs:

```python
result = run(video_path="demo.mp4", config=Config(frame_rate=2.0, image_format="png"))
```

Build a config from a dict — unknown keys are rejected:

```python
config = Config.from_dict({"frame_rate": 0.5, "language": "es", "quality": 80})
result = run(video_path="entrevista.mp4", config=config)
```

---

## ❹ Result

| Field            | Type             | Contains                        |
| ---------------- | ---------------- | ------------------------------- |
| `frame_count`    | `int`            | Frames written                  |
| `frames_dir`     | `Path` \| `None` | Frame output directory          |
| `transcript_dir` | `Path` \| `None` | Transcript output directory     |
| `segments`       | `list[Segment]`  | Timestamped transcript segments |

Each `Segment` carries `start` · `end` · `text`.

---

## ❺ Configuration

The transcription model is fixed internally — transcription behaves identically across every case. Everything below is adjustable.

| Option                  | Default        | Does                                   | Adjust when                                  |
| ----------------------- | -------------- | -------------------------------------- | -------------------------------------------- |
| `frame_rate`            | `1.0`          | Frames sampled per second              | Raise for fast motion, lower for screencasts |
| `quality`               | `85`           | webp and jpg quality, 1 to 100         | Lower to shrink files, raise for fidelity    |
| `compression_level`     | `6`            | webp and png effort, 0 to 6            | Lower for faster extraction on long videos   |
| `image_format`          | `"webp"`       | Frame format — `webp` `png` `jpg`      | Use `png` for lossless frames feeding OCR    |
| `frame_pattern`         | `"frame_%04d"` | printf stem for frame files            | Match an external naming scheme              |
| `language`              | `None`         | Language code, or auto detect          | Set when language is known to skip detection |
| `start_time`            | `None`         | First second to process                | Skip leading footage                         |
| `end_time`              | `None`         | Last second to process                 | Skip trailing footage                        |
| `output_root`           | `"output"`     | Base output directory                  | Redirect results elsewhere                   |
| `should_extract_frames` | `True`         | Extract frames                         | Disable to transcribe only                   |
| `should_transcribe`     | `True`         | Transcribe audio                       | Disable to extract frames only               |
| `should_write_manifest` | `True`         | Write the frame timestamp manifest     | Disable when only images are needed          |
| `should_time_words`     | `True`         | Word level timestamps for tight bounds | Disable for faster transcription             |

---

## ❻ Output Layout

```
output/<video_stem>/
├── frames/
│   ├── frame_0001.webp
│   └── manifest.json
└── transcript/
    └── transcript.json
```

---

## ❼ Command Line

```bash
clip-digest meeting.mp4 --frame-rate 2 --image-format png
clip-digest meeting.mp4 --only-transcript --language en
```

| Flag                | Default  | Does                                 |
| ------------------- | -------- | ------------------------------------ |
| `--output-root`     | `output` | Base output directory                |
| `--frame-rate`      | `1.0`    | Frames sampled per second            |
| `--quality`         | `85`     | webp and jpg quality, 1 to 100       |
| `--image-format`    | `webp`   | Frame format — `webp` `png` `jpg`    |
| `--language`        | auto     | Language code, or omit to detect     |
| `--start-time`      | none     | Trim start — `SS` `MM:SS` `HH:MM:SS` |
| `--end-time`        | none     | Trim end — `SS` `MM:SS` `HH:MM:SS`   |
| `--only-frames`     | off      | Extract frames only                  |
| `--only-transcript` | off      | Transcribe only                      |

---

## ❽ Errors

Branch on typed errors — all subclass `VideoDigestError`:

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

| Error                    | Raised when                          |
| ------------------------ | ------------------------------------ |
| `VideoNotFoundError`     | Video path does not exist            |
| `MissingDependencyError` | ffmpeg or whisper unavailable        |
| `ConfigError`            | Invalid or unknown config parameter  |
| `ExtractionError`        | Frame or transcript extraction fails |
| `VideoDigestError`       | Base class for all of the above      |
