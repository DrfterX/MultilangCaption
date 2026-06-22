# MultilangCaption

日本語・中文・English・한국어・粵語 のリアルタイム字幕オーバーレイ。  
A borderless, semi-transparent real-time multilingual subtitle overlay for **Windows 10**.

> **Why Windows 10?**  
> Windows 11 and macOS Sequoia already have built-in live captions.  
> This tool brings the same experience to Windows 10 — fully offline, no cloud required.

## Screenshot

```
┌─────────────────────────────────────────────┐
│  加藤さんには今ファンの消費期限のチェックを │
│  して値引きシールを貼る作業をやってもらって  │
└─────────────────────────────────────────────┘
         ↑ floating, semi-transparent ↑
```

## Quick Start

### 1. Install Python dependencies

```bash
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

### 2. Run

```bash
start_japanese.bat
```

First launch auto-downloads the SenseVoice model (~895MB, via ModelScope CDN, ~2 min).

## Features

- **Borderless overlay** — no title bar, drag to move, edge-drag to resize
- **Semi-transparent** — adjustable opacity (right-click menu)
- **Fill-to-edge wrapping** — text fills every pixel before wrapping (CHAR mode)
- **Always shows newest at bottom** — smooth incremental updates, no flicker
- **14 background colours + 11 font colours** — right-click to choose
- **Font size adjustable** — Ctrl+/- or right-click menu
- **Always-on-top toggle** — right-click menu
- **Zero console** — runs fully windowless via pythonw
- **Fully offline** — no internet needed after model download

## Supported Languages

The SenseVoice model auto-detects language. All five are recognised:

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
| `start_japanese.bat` | One-click launcher (auto-downloads model) |
| `subtitle_window.py` | Subtitle display overlay |
| `download_model.py` | Model downloader (ModelScope API, free & fast) |
| `requirements.txt` | Python dependencies |
| `vendor/` | Adapted TMSpeech ASR scripts |

## Model

SenseVoice multilingual model by Alibaba, converted to ONNX by [k2-fsa/sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx).

- `model.onnx` — 895MB (full precision)
- `tokens.txt` — 309KB vocabulary
- `silero_vad.onnx` — 629KB voice activity detection

Models are auto-downloaded on first run. No GitHub LFS required.

## Credits & License

- ASR pipeline adapted from [TMSpeech](https://github.com/jxlpzqc/TMSpeech) (MIT)
- Inference engine: [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) (Apache 2.0)
- Model hosting: [ModelScope](https://modelscope.cn)
- This project: MIT License
