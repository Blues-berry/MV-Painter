#!/usr/bin/env python3
"""Generate slide-synchronized V5 narration locally with Piper and FFmpeg.

Example:
  python build_v5_narrated_demo.py \
    --piper-bin /path/to/piper \
    --voice-model /path/to/en_US-lessac-medium.onnx
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path


OUT = Path(__file__).resolve().parent
SLIDES = OUT / "build" / "slides"
SCRIPT = OUT / "TCAS_Demo_V5_Narration_EN.md"
VIDEO_OUT = OUT / "TCAS_Demo_V5_Narrated.mp4"
SRT_OUT = OUT / "TCAS_Demo_V5_Narrated.srt"
PAUSE = 0.8
SENTENCE_PAUSE = 0.2


def run(args: list[str], *, input_text: str | None = None) -> str:
    result = subprocess.run(
        args,
        input=input_text,
        text=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def parse_script() -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    heading: str | None = None
    lines: list[str] = []
    for line in SCRIPT.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if heading is not None:
                entries.append((heading, " ".join(x.strip() for x in lines if x.strip())))
            heading, lines = line[3:].strip(), []
        elif heading is not None:
            lines.append(line)
    if heading is not None:
        entries.append((heading, " ".join(x.strip() for x in lines if x.strip())))
    if len(entries) != 10 or any(not body for _, body in entries):
        raise ValueError(f"Expected 10 non-empty slide scripts, found {len(entries)}")
    return entries


def slide_images(tmp: Path) -> list[Path]:
    images = [SLIDES / f"frame-{index:02}.png" for index in range(1, 11)]
    if all(image.is_file() for image in images):
        return images
    pdf = OUT / "TCAS_Demo_V5.pdf"
    prefix = tmp / "pdf-page"
    run(["pdftoppm", "-png", "-r", "144", str(pdf), str(prefix)])
    pages = sorted(
        tmp.glob("pdf-page-*.png"),
        key=lambda path: int(re.search(r"-(\d+)\.png$", path.name).group(1)),
    )
    if len(pages) != 10:
        raise RuntimeError(f"Expected 10 pages in {pdf}, found {len(pages)}")
    return pages


def duration(path: Path) -> float:
    value = run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ])
    return float(value)


def ffconcat_path(path: Path) -> str:
    return str(path.resolve()).replace("\\", "\\\\").replace("'", "\\'")


def srt_time(seconds: float) -> str:
    millis = round(seconds * 1000)
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def caption_chunks(text: str, max_words: int = 18) -> tuple[list[tuple[str, bool]], int]:
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]
    chunks: list[tuple[str, bool]] = []
    for sentence in sentences:
        words = sentence.split()
        pieces = [" ".join(words[start:start + max_words]) for start in range(0, len(words), max_words)]
        for index, piece in enumerate(pieces):
            chunks.append((piece, index == len(pieces) - 1))
    return chunks, len(sentences)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--piper-bin", required=True, type=Path)
    parser.add_argument("--voice-model", required=True, type=Path)
    parser.add_argument("--voice-config", type=Path)
    args = parser.parse_args()
    config = args.voice_config or Path(str(args.voice_model) + ".json")
    for required in (args.piper_bin, args.voice_model, config):
        if not required.is_file():
            raise FileNotFoundError(required)

    entries = parse_script()
    with tempfile.TemporaryDirectory(prefix="v5-piper-") as tmp_name:
        tmp = Path(tmp_name)
        images = slide_images(tmp)
        audio_files: list[Path] = []
        audio_durations: list[float] = []
        for index, (_, text) in enumerate(entries, start=1):
            wav = tmp / f"speech-{index:02}.wav"
            run([
                str(args.piper_bin), "--model", str(args.voice_model),
                "--config", str(config), "--output_file", str(wav), "--quiet",
            ], input_text=text)
            audio_files.append(wav)
            audio_durations.append(duration(wav))

        silence = tmp / "pause.wav"
        run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono",
            "-t", str(PAUSE), "-c:a", "pcm_s16le", str(silence), "-loglevel", "error",
        ])

        audio_concat = tmp / "audio.ffconcat"
        with audio_concat.open("w", encoding="utf-8") as stream:
            stream.write("ffconcat version 1.0\n")
            for wav in audio_files:
                stream.write(f"file '{ffconcat_path(wav)}'\n")
                stream.write(f"file '{ffconcat_path(silence)}'\n")
        merged_audio = tmp / "narration.wav"
        run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(audio_concat),
            "-c:a", "pcm_s16le", str(merged_audio), "-loglevel", "error",
        ])
        attenuated_audio = tmp / "narration_attenuated.wav"
        run([
            "ffmpeg", "-y", "-i", str(merged_audio), "-af", "volume=-3dB",
            "-c:a", "pcm_s16le", str(attenuated_audio), "-loglevel", "error",
        ])

        video_concat = tmp / "video.ffconcat"
        slide_durations = [length + PAUSE for length in audio_durations]
        with video_concat.open("w", encoding="utf-8") as stream:
            stream.write("ffconcat version 1.0\n")
            for image, length in zip(images, slide_durations):
                stream.write(f"file '{ffconcat_path(image)}'\n")
                stream.write(f"duration {length:.6f}\n")
            stream.write(f"file '{ffconcat_path(images[-1])}'\n")
        total = sum(slide_durations)
        silent_video = tmp / "video.mp4"
        run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(video_concat),
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p",
            "-t", f"{total:.6f}", "-c:v", "libx264", "-preset", "medium",
            "-crf", "21", "-an", str(silent_video), "-loglevel", "error",
        ])
        run([
            "ffmpeg", "-y", "-i", str(silent_video), "-i", str(attenuated_audio),
            "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
            "-b:a", "128k", "-movflags", "+faststart", "-shortest", str(VIDEO_OUT),
            "-loglevel", "error",
        ])

        cues: list[str] = []
        start = 0.0
        cue_number = 0
        for (_, text), length in zip(entries, audio_durations):
            chunks, sentence_count = caption_chunks(text)
            total_words = sum(len(chunk.split()) for chunk, _ in chunks)
            estimated_speech = max(length - SENTENCE_PAUSE * sentence_count, length * 0.8)
            cursor = start
            for chunk, sentence_end in chunks:
                chunk_duration = estimated_speech * len(chunk.split()) / total_words
                cue_number += 1
                cues.extend([
                    str(cue_number),
                    f"{srt_time(cursor)} --> {srt_time(cursor + chunk_duration)}",
                    chunk,
                    "",
                ])
                cursor += chunk_duration
                if sentence_end:
                    cursor += SENTENCE_PAUSE
            start += length + PAUSE
        SRT_OUT.write_text("\n".join(cues), encoding="utf-8")

        output_duration = duration(VIDEO_OUT)
        streams = json.loads(run([
            "ffprobe", "-v", "error", "-show_streams", "-of", "json", str(VIDEO_OUT),
        ]))["streams"]
        video = next(stream for stream in streams if stream["codec_type"] == "video")
        audio = next(stream for stream in streams if stream["codec_type"] == "audio")
        if (video["width"], video["height"], video["r_frame_rate"]) != (1920, 1080, "30/1"):
            raise RuntimeError(f"Unexpected video stream: {video}")
        if audio["sample_rate"] != "22050" or audio["channels"] != 1:
            raise RuntimeError(f"Unexpected narration stream: {audio}")
        if abs(output_duration - total) > 0.12:
            raise RuntimeError(f"Audio/video duration mismatch: {output_duration:.3f} vs {total:.3f}s")
        print(json.dumps({
            "video": str(VIDEO_OUT),
            "subtitles": str(SRT_OUT),
            "slides": len(entries),
            "duration_seconds": round(output_duration, 3),
            "voice": "en_US-lessac-medium",
            "disclosure_in_opening": entries[0][1].startswith("This demo uses AI-generated narration."),
        }, indent=2))


if __name__ == "__main__":
    main()
