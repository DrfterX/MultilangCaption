#!/usr/bin/env python3
"""Download required models via ModelScope API (fast, free, no login needed)."""
import os, sys, urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(SCRIPT_DIR, "models")

MODELS = {
    # (local_subpath, remote_url)
    "silero_vad.onnx": (
        "https://modelscope.cn/api/v1/models/pengzhendong/sherpa-onnx-sense-voice-zh-en-ja-ko-yue/repo?Revision=master&FilePath=silero_vad.onnx",
    ),
    "sense_voice/model.onnx": (
        "https://modelscope.cn/api/v1/models/pengzhendong/sherpa-onnx-sense-voice-zh-en-ja-ko-yue/repo?Revision=master&FilePath=model.onnx",
    ),
    "sense_voice/tokens.txt": (
        "https://modelscope.cn/api/v1/models/pengzhendong/sherpa-onnx-sense-voice-zh-en-ja-ko-yue/repo?Revision=master&FilePath=tokens.txt",
    ),
}

# VAD model from GitHub (small, 629KB) — fallback URL
VAD_FALLBACK = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx"

def download(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print(f"  Downloading {os.path.basename(dest)} ...", end=" ", flush=True)
    try:
        urllib.request.urlretrieve(url, dest)
        size_mb = os.path.getsize(dest) / (1024 * 1024)
        print(f"OK ({size_mb:.1f} MB)")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def main():
    missing = False
    for fname, (url,) in MODELS.items():
        dest = os.path.join(MODEL_DIR, fname)
        if os.path.exists(dest):
            size = os.path.getsize(dest)
            if fname.endswith(".onnx") and size < 10 * 1024 * 1024:
                print(f"  {fname} seems incomplete ({size} bytes), re-downloading...")
                os.remove(dest)
            else:
                print(f"  {fname} already exists, skip")
                continue

        if not download(url, dest):
            # VAD fallback
            if "silero_vad" in fname:
                print("  Trying fallback URL...", end=" ", flush=True)
                download(VAD_FALLBACK, dest)
            missing = True

    if not missing:
        print("\nAll models ready.")

if __name__ == "__main__":
    main()
