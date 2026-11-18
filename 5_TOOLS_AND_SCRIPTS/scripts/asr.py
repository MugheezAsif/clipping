"""GPU word-level transcription (faster-whisper large-v3-turbo) -> words.json [[ms, "word"], ...]
Run with the clipping venv:  ~/.clipping/env/Scripts/python.exe asr.py <media> <words.json> [--lang en]
"""
import json, os, sys, glob

env = os.path.dirname(os.path.dirname(sys.executable))
for d in glob.glob(os.path.join(env, "Lib", "site-packages", "nvidia", "*", "bin")):  # cuBLAS / cuDNN DLLs from pip
    os.add_dll_directory(d); os.environ["PATH"] = d + os.pathsep + os.environ["PATH"]
from faster_whisper import WhisperModel, BatchedInferencePipeline

src, out = sys.argv[1], sys.argv[2]
lang = sys.argv[sys.argv.index("--lang") + 1] if "--lang" in sys.argv else "en"
try:
    m = WhisperModel("large-v3-turbo", device="cuda", compute_type="float16")
except Exception as e:  # CPU fallback keeps the pipeline working
    print("GPU unavailable, using CPU:", str(e)[:120]); m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
import subprocess, numpy as np  # decode with ffmpeg (avoids PyAV version issues)
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
segs, info = BatchedInferencePipeline(model=m).transcribe(audio, language=lang, word_timestamps=True, batch_size=16, vad_filter=True)
words = [[int(w.start * 1000), w.word.strip()] for s in segs for w in (s.words or []) if w.word.strip()]
json.dump(words, open(out, "w", encoding="utf-8"))
print(f"{len(words)} words, {info.duration:.0f}s audio")
