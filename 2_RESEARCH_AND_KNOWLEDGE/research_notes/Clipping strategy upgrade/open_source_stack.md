# Open-source auto-clipping stack (Win11 + RTX 5080, checked 2026-11-17)

Stars, last push and license come from the GitHub API on 2026-11-17. Wheel and Python support comes from the PyPI JSON on the same date.

## End-to-end repos: what's alive and what to borrow

### Takeaway
No repo beats our hand-tuned pipeline on quality. The best ideas to borrow come from **OpenShorts** (per-scene layout modes), **Clips Kitty** (multi-signal scoring with an LLM head-to-head rerank, and TalkNet speaker-cut instead of pan), and **AI-Youtube-Shorts-Generator** (an editable virality rubric prompt). Avoid repos that are stale (ClipsAI, reels-clips-automator) or faceless-video generators (MoneyPrinterTurbo, ShortGPT).

### Cited Findings
- **mutonby/openshorts**: 8.8k stars, pushed 2026-11-17, MIT. Uses faster-whisper large-v3-turbo (Parakeet is an optional GPU backend). Gemini 3.1 Flash-Lite ranks the transcript plus scene boundaries into 3-15 moments of 15-60 s; `LLM_BASE_URL` accepts any OpenAI-compatible server (Ollama, LM Studio). Face tracking uses MediaPipe + YOLOv8, scene cuts use PySceneDetect. Each scene gets one of 4 layouts: TRACK, GENERAL (blurred background), SPLIT (2 speakers stacked, captions on the seam) and SCREENCAST. Ships as Docker (Python 3.11); on Windows it runs only through Docker Desktop/WSL2; there's also `pip install openshorts` and an MCP mode — [GitHub](https://github.com/mutonby/openshorts)
- **Anil-matcha/AI-Youtube-Shorts-Generator** (old SamurAIGPT URL redirects here): 6.2k stars, pushed 2026-11-12, MIT, Python 3.10+. Local mode uses faster-whisper, an OpenCV face tracker with motion smoothing, and gpt-4o-mini or gemini-2.5-flash. It splits videos over 30 min into 20-min chunks with 60 s overlap and dedups candidates that overlap >50% (keeps the higher score) — [GitHub](https://github.com/Anil-matcha/AI-Youtube-Shorts-Generator)
  - Rubric in `shorts_generator/highlights.py`, 8 signals ranked by impact: hooks, emotional peaks, "opinion bombs", revelations/confessions, conflict, quotable one-liners, story payoff, practical value. The output is JSON `{title,start_time,end_time,score 0-100,hook_sentence,virality_reason}`. Rules: hook within ~3 s, complete thoughts only, no overlap, 45-90 s target (20-44 s only for one-liners) — [highlights.py](https://raw.githubusercontent.com/Anil-matcha/AI-Youtube-Shorts-Generator/main/shorts_generator/highlights.py)
- **ColinGPT9/clips-studio ("Clips Kitty")**: 298 stars, pushed 2026-11-17, **AGPL-3.0**. Native Windows app (`winget install ColinGPT9.ClipsKitty`). Uses faster-whisper large-v3-turbo with word timestamps, plus 5 per-second signals normalized within each video: audio, visual, reaction, hook and payoff. YouTube most-replayed data adds a capped bonus. The LLM scores clips 0-100, then **reranks the finalists head-to-head in one call** ("relative comparison suits smaller models"). YOLOv8-pose handles the crop, and **TalkNet ASD picks who to follow; a speaker change triggers a cut, not a pan**. Podcast mode gives each shot its own steady crop. NVIDIA needs a CUDA 13 torch build — [GitHub](https://github.com/ColinGPT9/clips-studio)
- **modelscope/FunClip**: 6.6k stars, pushed 2026-11-01, MIT. FunASR Paraformer is strongest on Chinese (English via `-l en`, Fun-ASR-Nano or SenseVoice). CAM++ speaker IDs let you clip by speaker. LLM clipping, Gradio UI, Python 3.12; Whisper support is listed as "coming soon". Weak fit for English MrBeast-style content — [GitHub](https://github.com/modelscope/FunClip)
- **ClipsAI/clipsai**: 575 stars, **last push 2024-01-17**, MIT. Resize combines pyannote diarization, PySceneDetect and MTCNN/MediaPipe faces — [GitHub](https://github.com/ClipsAI/clipsai), [docs](https://clipsai.com/references/resize). Clip finding via TextTiling is reported only by third-party sites — [search summary](https://60minuteapps-directory.pages.dev/tool/clipsai/)
- **eddieoz/reels-clips-automator**: 235 stars, last push 2023-09-23. Stale — [GitHub](https://github.com/eddieoz/reels-clips-automator)
- **RayVentura/ShortGPT** (8.2k stars, last push 2025-02-10) and **harry0703/MoneyPrinterTurbo** (144k stars, active, MIT) — [ShortGPT](https://github.com/RayVentura/ShortGPT), [MPT](https://github.com/harry0703/MoneyPrinterTurbo)
- Other 2026 repos are small: xixihhhh/hotclip (474 stars, AGPL, Chinese livestream slicing), fralapo/clippyme (67), kleZ799/clipmint (48), lowdevco/Clip-Forge (55, a Claude skill), Anil-matcha/ai-clipping-comfyui (39) — [GitHub search API](https://api.github.com/search/repositories?q=youtube+shorts+clips+in:name,description&sort=stars)

### Inferences
- ShortGPT and MoneyPrinterTurbo are faceless generators (stock footage + TTS), not long-to-short clippers. Skip them. I'm basing this on my prior knowledge of their READMEs; I didn't re-fetch them.
- Ideas worth copying into `5_TOOLS_AND_SCRIPTS/scripts/`:
  - the Clips Kitty pattern: per-second signals → candidate windows → LLM 0-100 score → head-to-head rerank of the top ~10
  - the Anil-matcha rubric fields, adapted to our "payoff + one emotion" rule
  - OpenShorts' layout-per-scene with a SPLIT fallback
  - the >50% overlap dedup
- AGPL code (Clips Kitty, hotclip, ultralytics) is fine to run locally. Copy ideas, not code.

### Gaps
- No public quality benchmark compares these tools. The quality claims are the maintainers' own.

## Building blocks: best current choices

### Takeaway
ASR: keep whisper.cpp, or move to **faster-whisper large-v3-turbo + word_timestamps** (it's what every active repo uses). Scene cuts: **PySceneDetect**. Faces: **MediaPipe**, with YOLOv8 as a fallback. ASD: **Light-ASD/TalkNet** only for multi-speaker podcasts. Silence: **auto-editor**. Captions: keep HyperFrames/ASS.

### Cited Findings
- **faster-whisper** (26.8k stars, MIT, v1.2.1). `word_timestamps=True` gives per-word start/end. `BatchedInferencePipeline(batch_size=8-16)` turns on VAD by default and cut large-v2 from 1m03s to 17s for about +1.5 GB VRAM. GPU needs cuBLAS for CUDA 12 and cuDNN 9. On Windows, use Purfview's whisper-standalone-win DLL bundle on PATH — [GitHub](https://github.com/SYSTRAN/faster-whisper). ctranslate2 4.9.0 (2026-11-10) ships Windows wheels for cp310-cp315 — [PyPI](https://pypi.org/pypi/ctranslate2/json)
- **WhisperX** (25.4k stars, BSD-2). Adds wav2vec2 phoneme alignment for tighter word times; words containing digits or symbols get no timing. Diarization runs through pyannote community-1. The README asks for the CUDA 12.8 toolkit and claims 70x realtime — [GitHub](https://github.com/m-bain/whisperX). The latest release 3.8.6 declares **`requires_python <3.14,>=3.10`** — [PyPI](https://pypi.org/pypi/whisperx/json)
- **whisper.cpp**: 55k stars, active — [GitHub](https://github.com/ggml-org/whisper.cpp)
- **pyannote-audio** (10.8k stars, MIT, 4.1.0, Python ≥3.11). `speaker-diarization-community-1` needs a Hugging Face token plus accepting the model's conditions. Audio decoding uses torchcodec, which needs ffmpeg. On an H100 it runs at 31 s per hour of audio — [GitHub](https://github.com/pyannote/pyannote-audio). torchcodec 0.17 has Windows wheels for cp311-cp314 — [PyPI](https://pypi.org/pypi/torchcodec/json)
- **PySceneDetect** (5.5k stars, BSD-3, 0.7.3, 2026-11-08) is used by OpenShorts and ClipsAI — [GitHub](https://github.com/Breakthrough/PySceneDetect). **TransNetV2** (1.1k stars) was last pushed in 2023 — [GitHub](https://github.com/soCzech/TransNetV2)
- **Face and person tracking**:
  - MediaPipe: Apache-2.0, very active — [GitHub](https://github.com/google-ai-edge/mediapipe)
  - ultralytics YOLO: **AGPL-3.0** — [GitHub](https://github.com/ultralytics/ultralytics)
  - InsightFace: code has no SPDX license; pretrained models are non-commercial per the repo — [GitHub](https://github.com/deepinsight/insightface)
- **Active speaker detection**:
  - Light-ASD reaches 94.06% mAP on AVA validation, and `Columbia_test.py` runs on any mp4. No requirements file; last push 2025-03 — [GitHub](https://github.com/Junhua-Liao/Light-ASD)
  - LR-ASD: same author, 149 stars, last push 2025-03 — [GitHub](https://github.com/Junhua-Liao/LR-ASD)
  - TalkNet-ASD: 520 stars, last push 2023 — [GitHub](https://github.com/TaoRuijie/TalkNet-ASD)
- **auto-editor** (6k stars, Unlicense, active). Now written in Nim (`ae.nimble`); PyPI's latest is 29.3.1 from 2025-11. Example flags: `--edit audio:threshold=0.04`, `audio:-19dB`, `--edit "(or audio:0.03 motion:0.06)"`, `--margin 0.2sec`. Exports to `--export premiere|resolve|final-cut-pro|edl|clip-sequence` — [GitHub](https://github.com/WyattBlue/auto-editor)
- **pycaps** (233 stars, MIT, alpha). Install from git: `pip install "git+https://github.com/francozanardi/pycaps.git#egg=pycaps[all]"`. The PyPI name `pycaps` belongs to an unrelated 2017 package. CSS captions render through Playwright Chromium. Tested only on **Python 3.10-3.12**. CLI: `pycaps render --input x.mp4 --template minimalist --transcript t.json` — [GitHub](https://github.com/francozanardi/pycaps)
- **Laughter detection**: jrgillick/laughter-detection v2.0 (Interspeech 2021) runs via `segment_laughter.py`, but was tested on PyTorch 1.3 and Python 3.6 — [GitHub](https://www.github.com/jrgillick/laughter-detection), [paper](https://www.isca-archive.org/interspeech_2021/gillick21_interspeech.html)
- **stable-ts** is now **archived** — [GitHub](https://github.com/jianfch/stable-ts)

### Inferences
- pycaps duplicates our HyperFrames captions. Skip it; ASS via ffmpeg `subtitles=` is the zero-install fallback.
- Excitement signal with no new install: ffmpeg `ebur128` short-term loudness (M/S) per second, plus the rate of words per second from the transcript, plus `[laughter]`/`[applause]` style tokens from Whisper. Add PANNs/YAMNet AudioSet tagging (Laughter, Cheering, Applause, Screaming) only if needed. This is unverified; PANNs wasn't researched here.
- Our content (MrBeast-style, often one presenter per shot) mostly needs a face-centred crop per scene. Full ASD is overkill except for two-person sit-downs.

### Gaps
- I found no maintained pip package for Light-ASD or TalkNet; the demos are research scripts with old dependencies.
- PANNs and YAMNet were not checked.

## Windows + RTX 50 (sm_120) gotchas

### Takeaway
Use torch from the **cu128 or newer index**, never default PyPI. On Windows the default PyPI torch wheel is CPU-only, a long-standing fact. Give faster-whisper/CTranslate2 the CUDA 12 cuBLAS + cuDNN 9 DLLs on PATH. Run anything that needs Python <3.14 (WhisperX, pycaps, ASD demos) in a 3.12 venv.

### Cited Findings
- Stable PyTorch builds made with older CUDA lack sm_120 kernels ("not compatible", arch list stops at sm_90). cu128 builds fixed it for 5080/5070 Ti users — [PyTorch forum](https://discuss.pytorch.org/t/pytorch-support-for-sm120/216099?page=3), [5070 Ti Windows](https://discuss.pytorch.org/t/pytorch-support-for-sm120/216099/81)
- If torch works but a workload still says "no kernel image", the culprit is a separately compiled extension such as xformers, flash-attn or bitsandbytes — [localaimaster](https://localaimaster.com/blog/no-kernel-image-available-rtx-50)
- WhisperX moved to torch 2.7.1, CUDA 12.8 and CTranslate2 ≥4.5.0, and was reported working on sm_120. That report is from a user, not official release notes — [whishper#172](https://github.com/pluja/whishper/issues/172)
- torch 2.15.0 (2026-10-28) has Windows cp311-cp315 wheels. onnxruntime-gpu 1.32 has Windows cp311-cp314 wheels — [torch PyPI](https://pypi.org/pypi/torch/json), [ORT PyPI](https://pypi.org/pypi/onnxruntime-gpu/json)
- Clips Kitty targets a CUDA 13 torch build plus cuBLAS 12 on Windows — [GitHub](https://github.com/ColinGPT9/clips-studio)

### Gaps
- I couldn't confirm the exact CUDA index tag for torch 2.15 (cu128/cu129/cu130). Pick it on pytorch.org "Get Started", then verify `torch.cuda.get_arch_list()` contains `sm_120`.
- I found no official CTranslate2 changelog line naming sm_120.

## Recommendation: minimal stack

### Takeaway
Two installs cover about 90% of the value: faster-whisper (or keep whisper.cpp) and PySceneDetect + MediaPipe for scene-aware face crops. Everything else is prompts and ffmpeg.

### Cited Findings
- Install commands, Python 3.14 main venv (wheels confirmed above):
  ```
  winget install Gyan.FFmpeg            # already have
  py -3.14 -m venv .venv && .venv\Scripts\activate
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128   # or newer cuXXX per pytorch.org
  pip install faster-whisper nvidia-cublas-cu12 nvidia-cudnn-cu12==9.*   # then add site-packages\nvidia\{cublas,cudnn}\bin to PATH
  pip install "scenedetect[opencv]" mediapipe
  pip install pyannote.audio            # only if 2-speaker clips; needs HF token
  ```
- Optional extras:
  - auto-editor: Nim binary, see auto-editor.com/installing — [GitHub](https://github.com/WyattBlue/auto-editor)
  - WhisperX in a `py -3.12` venv, because of the `<3.14` pin — [PyPI](https://pypi.org/pypi/whisperx/json)
  - Ollama for a local LLM via OpenShorts' OpenAI-compatible pattern — [OpenShorts](https://github.com/mutonby/openshorts)

### Inferences
Pipeline to adopt:
1. yt-dlp, then whisper.cpp or faster-whisper large-v3-turbo with word timestamps.
2. PySceneDetect `detect-content` for cut list.
3. Per-second signal table: ebur128 loudness, words/s, laughter tokens, scene density and YouTube most-replayed data when available.
4. LLM (Claude) gets the transcript chunked into 20-min windows with 60 s overlap, plus the signal peaks. It scores with the 0-100 rubric and our fields (payoff, emotion, hook ≤6 words, cold-open timestamp).
5. Dedup at >50% overlap, then a head-to-head rerank of the top 10, then pick 5.
6. MediaPipe face boxes per scene → steady crop per scene (no panning), with blurred-bg fallback when there are no faces or more than 2 faces.
7. Render with HyperFrames/ffmpeg as today.

Don't adopt any full repo; borrow the scoring and crop logic only.

### Gaps
- No RTX 5080 benchmark was found for faster-whisper vs whisper.cpp turbo. Measure locally before switching ASR.
