# MultilangCaption

**English** | [中文](README_CN.md)

A borderless, semi-transparent real-time multilingual subtitle overlay for **Windows 10**.

> **Why Windows 10?**  
> Windows 11 and macOS Sequoia already have built-in live captions.  
> This tool brings the same experience to Windows 10 — fully offline, no cloud required.

Supports: 中文 · English · 日本語 · 한국어 · 粵語

## Quick Start

```bash
# 1. Install dependencies
python -m venv venv
venv\Scripts\pip install -r requirements.txt

# 2. Launch
start_japanese.bat
```

First launch auto-downloads the SenseVoice model (~895MB, via ModelScope CDN, ~2 min).  
The overlay appears at the bottom-centre of your screen, auto-capturing your system audio.

## Choosing Audio Device

| Launcher | Behaviour |
|----------|-----------|
| **`start_japanese.bat`** | Default. Auto-selects your system speaker (loopback). No prompts. |
| **`start_japanese_advanced.bat`** | Opens a device picker — choose speaker, microphone, or both. For multi-device setups. |

## Features

- **Borderless overlay** — no title bar; drag to move, edge-drag to resize
- **Semi-transparent** — adjustable opacity (right-click menu)
- **Fill-to-edge wrapping** — text fills every pixel before wrapping (CHAR mode)
- **Always shows newest at bottom** — smooth incremental updates, no flicker
- **14 background colours + 11 font colours** — right-click to choose
- **Font size adjustable** — Ctrl+/- or right-click menu
- **Always-on-top toggle** — right-click menu
- **Zero console** — runs fully windowless via pythonw
- **Fully offline** — no internet needed after model download
- **Remembers settings** — font, colours, opacity, window position & size persist across restarts

## Supported Languages

The SenseVoice model auto-detects language:

| Language | Code |
|----------|------|
| Chinese  | zh   |
| English  | en   |
| Japanese | ja   |
| Korean   | ko   |
| Cantonese| yue  |

## How It Works

```
System Audio → WASAPI Loopback → SenseVoice ASR → status file → tkinter overlay
```

- Audio capture: PyAudioWPatch (WASAPI loopback)
- Speech recognition: [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) + SenseVoice
- ASR pipeline: adapted from [TMSpeech](https://github.com/jxlpzqc/TMSpeech)
- Display: custom tkinter borderless overlay window

## Files

| File | Purpose |
|------|---------|
| `start_japanese.bat` | One-click launcher (auto-device, auto-downloads model) |
| `start_japanese_advanced.bat` | Launcher with manual device picker |
| `subtitle_window.py` | Subtitle display overlay |
| `download_model.py` | Model downloader (ModelScope API, free & fast) |
| `requirements.txt` | Python dependencies |
| `vendor/` | Adapted TMSpeech ASR scripts |

## Model

SenseVoice multilingual model by Alibaba, converted to ONNX by [k2-fsa/sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx).

- `model.onnx` — 895MB
- `tokens.txt` — 309KB
- `silero_vad.onnx` — 629KB

Auto-downloaded on first run. No GitHub LFS needed.

## Credits & License

- ASR pipeline adapted from [TMSpeech](https://github.com/jxlpzqc/TMSpeech) (MIT)
- Inference engine: [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) (Apache 2.0)
- Model hosting: [ModelScope](https://modelscope.cn)
- This project: MIT License
