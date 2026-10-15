# V5 presentation and demo

These companion files follow the current V5 manuscript and are separate from the journal `UPLOAD_FILES` directory.

- `TCAS_Demo_V5.pptx`: editable 10-slide deck; speaker notes match the narration script.
- `TCAS_Demo_V5.pdf`: review copy of the deck.
- `TCAS_Demo_V5_Silent.mp4`: 90-second, 1080p silent slideshow demo.
- `TCAS_Demo_V5_Narrated.mp4`: slide-synchronized 1080p demo with English narration.
- `TCAS_Demo_V5_Narrated.srt`: sentence-level English subtitles timed within the narration segments.
- `TCAS_Demo_V5_Still.png`: baked-asset slide preview.
- `TCAS_Demo_V5_Narration_EN.md`: slide-by-slide English voiceover script and voice method.
- `build_v5_demo.py`: rebuilds the deck and silent video from the V5 figure PDFs.
- `build_v5_narrated_demo.py`: regenerates the narrated MP4 and subtitles from the script, deck PDF, and a local Piper voice model.

The narrated MP4 uses local Piper TTS with the en_US-lessac-medium voice; the opening sentence discloses AI-generated narration. The older 0907 audio was not reused because it does not match V5. Download the Piper executable from [rhasspy/piper releases](https://github.com/rhasspy/piper/releases) and the voice model from [rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/lessac/medium). The voice-model repository identifies its license as MIT.

To regenerate the narration, install `ffmpeg`, `ffprobe`, and `pdftoppm`, then run `python build_v5_narrated_demo.py --piper-bin /path/to/piper --voice-model /path/to/en_US-lessac-medium.onnx`. The script renders its ten slide images from the deck PDF when cached images are unavailable.

The display examples are illustrative. All quantitative claims are taken from V5; no experimental results or cohort statistics were changed.
