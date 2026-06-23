# MultilangCaption

[English](README.md) | **中文**

为 **Windows 10** 打造的无边框半透明多语言实时字幕浮窗。

> **为什么是 Windows 10？**  
> Windows 11 和 macOS Sequoia 已内置实时字幕。  
> 本工具为 Windows 10 用户提供同样体验 — 完全离线，无需联网。

支持：中文 · English · 日本語 · 한국어 · 粵語

## 快速开始

```bash
# 1. 安装依赖
python -m venv venv
venv\Scripts\pip install -r requirements.txt

# 2. 启动
start_japanese.bat
```

首次运行自动下载 SenseVoice 模型（约 895MB，通过 ModelScope CDN，约 2 分钟）。  
字幕浮窗自动出现在屏幕底部居中位置，默认捕获系统音频。

## 音频设备选择

| 启动文件 | 行为 |
|---------|------|
| **`start_japanese.bat`** | 默认。自动选择系统扬声器回环设备，无需任何操作。 |
| **`start_japanese_advanced.bat`** | 弹出设备选择窗口，可手动选择扬声器、麦克风或同时多选。适合多设备用户。 |

## 功能特性

- **无边框浮窗** — 无标题栏，鼠标拖拽移动，边缘拖拽调整大小
- **半透明可调** — 右键菜单调整不透明度
- **填满再换行** — 文字填满窗口宽度后自动折行（按字符）
- **最新字幕始终在底部** — 平滑增量更新，不闪烁
- **14 种底色 + 11 种字体颜色** — 右键菜单一键切换
- **字号可调** — Ctrl+/- 或右键菜单
- **窗口置顶** — 右键菜单切换
- **零控制台** — pythonw 运行，无黑窗
- **完全离线** — 模型下载后无需联网
- **设置记忆** — 字体、颜色、透明度、窗口位置和大小自动保存，下次启动恢复

## 支持语言

SenseVoice 模型自动检测语言：

| 语言 | 代码 |
|------|------|
| 中文 | zh |
| 英语 | en |
| 日语 | ja |
| 韩语 | ko |
| 粤语 | yue |

## 工作原理

```
系统音频 → WASAPI 回环采集 → SenseVoice 语音识别 → 状态文件 → tkinter 浮窗
```

- 音频采集：PyAudioWPatch（WASAPI 回环）
- 语音识别：[sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) + SenseVoice
- ASR 管线：改编自 [TMSpeech](https://github.com/jxlpzqc/TMSpeech)
- 显示：自研 tkinter 无边框浮窗

## 文件说明

| 文件 | 用途 |
|------|------|
| `start_japanese.bat` | 一键启动（自动设备，自动下载模型） |
| `start_japanese_advanced.bat` | 启动（手动选择音频设备） |
| `subtitle_window.py` | 字幕显示浮窗 |
| `download_model.py` | 模型下载器（ModelScope API，免费高速） |
| `requirements.txt` | Python 依赖 |
| `vendor/` | 改编自 TMSpeech 的 ASR 脚本 |

## 模型

阿里 SenseVoice 多语言模型，由 [k2-fsa/sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) 转换为 ONNX 格式。

- `model.onnx` — 895MB
- `tokens.txt` — 309KB
- `silero_vad.onnx` — 629KB

首次运行自动下载，无需 GitHub LFS。

## 致谢 & 开源协议

- ASR 管线改编自 [TMSpeech](https://github.com/jxlpzqc/TMSpeech)（MIT）
- 语音模型：阿里 [FunAudioLLM/SenseVoice](https://github.com/FunAudioLLM/SenseVoice)
- 推理引擎：[sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx)（Apache 2.0）
- 模型托管：[ModelScope](https://modelscope.cn)
- 本项目：MIT License
