@echo off
set "SD=%~dp0"
set "PY=%SD%venv\Scripts\python.exe"
set "PYW=C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\pythonw.exe"

set "SC=%SD%vendor\simulate-streaming-sense-voice.py"
set "SV=%SD%models\sense_voice\model.onnx"
set "TK=%SD%models\sense_voice\tokens.txt"
set "VD=%SD%models\silero_vad.onnx"
set "SF=%SD%subtitle_status.txt"
set "DW=%SD%subtitle_window.py"
set "DL=%SD%download_model.py"

echo === TMSpeech Japanese Subtitles ===
echo.

if not exist "%PY%" (
    echo [ERROR] Python venv not found. Please run: python -m venv venv
    echo         Then: venv\Scripts\pip install sherpa-onnx PyAudioWPatch scipy
    pause & exit /b 1
)

if not exist "%SV%" (
    echo [INFO] Models not found, downloading...
    "%PY%" "%DL%"
    if not exist "%SV%" (
        echo [ERROR] Model download failed.
        pause & exit /b 1
    )
)

if not exist "%PYW%" (
    set "PYW=%PY%"
)

type nul > "%SF%"
start "" "%PYW%" "%DW%" -- "%PY%" "%SC%" --sense-voice="%SV%" --tokens="%TK%" --silero-vad-model="%VD%" --num-threads=4 --mix-mode=average --status-file="%SF%"
