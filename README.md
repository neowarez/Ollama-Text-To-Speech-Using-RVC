# Ollama-Text-To-Speech-Using-RVC

# 🎙️ Ollama + Piper + RVC + Vosk Voice Assistant (Windows)

This project is a proof-of-concept voice assistant that connects:

- **[Ollama](https://ollama.ai/)** → local LLMs (tested with `moondream`)
- **[Piper TTS](https://github.com/rhasspy/piper)** → fast neural text-to-speech
- **[Retrieval-based Voice Conversion (RVC)](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)** → converts Piper’s voice into a custom trained one (e.g. cartoon/celebrity/your dataset)
- **[Vosk](https://alphacephei.com/vosk/)** → offline speech-to-text for optional “voice control mode”

💡 The flow:
User → (Ollama response) → Piper TTS → Audio Fix (ffmpeg) → RVC Voice Conversion → Playback


---

## 📦 Requirements

- **Python 3.10+**
- **ffmpeg** → install from [gyan.dev builds](https://www.gyan.dev/ffmpeg/builds/)
- **Piper TTS** → download `piper.exe` and voice models (`.onnx`)
- **RVC WebUI** → clone repo and place your trained models
- **Vosk model** (optional, for STT) → download [vosk-model-small-en-us-0.15](https://alphacephei.com/vosk/models)

---

## 🔧 Setup

1. **Clone this repo**  
   ```bash
   git clone https://github.com/neowarez/ollama-rvc-voice-assistant.git
   cd ollama-rvc-voice-assistant

Create virtual environment

python -m venv venv310
venv310\Scripts\activate


Install Python dependencies

pip install -r requirements.txt


Install ffmpeg (system-wide)

Download from: https://www.gyan.dev/ffmpeg/builds/

Extract, add bin/ to your PATH.

Verify:

ffmpeg -version


Download Piper

Grab piper.exe from releases
.

Place it in C:\piper\.

Download voice models (.onnx) into C:\piper\models\.

Test:

echo Hello world | C:\piper\piper.exe --model C:\piper\models\en_US-amy-medium.onnx --output_file test.wav


Download RVC WebUI

For Nvidia GPU users:
https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/RVC1006Nvidia.7z

For AMD/Intel GPU users:
https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/RVC1006AMD_Intel.7z

create a folder called RVC -- optional
create another folder called models -- use this folder as a place to store your trained voice models, you will still need to put your trained .pth and .index models here: C:\RVC\RVC1006AMD_Intel\models\

Put your trained .pth + .index models in C:\RVC\RVC1006AMD_Intel\models\

Download Vosk (optional)

Unzip vosk-model-small-en-us-0.15 into D:\

Update path in script:

VOSK_MODEL_PATH = r"D:\vosk-model-small-en-us-0.15"

🚀 Running

Start Ollama in the background:

ollama serve


Run the assistant:

python ollama_tts.py


Type messages or activate voice mode:

Type a message (/bye to quit): hello there!
Type a message (/bye to quit): activate voice control
🎤 Voice control enabled! Speak freely.

⚙️ Config

Inside ollama_tts.py, update paths:

# Piper
PIPER_EXE = r"C:\piper\piper.exe"
PIPER_MODEL = r"C:\piper\models\en_US-amy-medium.onnx"

# RVC
PYTHON_EXE = r"C:\ollamatts\venv310\Scripts\python.exe"
RVC_SCRIPT = r"D:\RVC\Retrieval-based-Voice-Conversion-WebUI\tools\infer_cli.py"
RVC_PTH = r"D:\RVC\RVC1006AMD_Intel\models\PrincessBubblegumv1_best.pth"
RVC_INDEX = r"D:\RVC\RVC1006AMD_Intel\models\PrincessBubblegumv1.index"

# Vosk
VOSK_MODEL_PATH = r"D:\vosk-model-small-en-us-0.15"

# Ollama
MODEL_NAME = "your_model_here"

📜 requirements.txt

```bash

torch>=2.0.0
numpy
sounddevice
soundfile
requests
vosk
fairseq
librosa
av
ffmpeg-python
colorama

```

📝 Notes

Piper runs fast even on CPU.

RVC is set to run on CPU (--device cpu), but change to cuda:0 if you have an NVIDIA GPU.

This is Windows-specific (tested on Win10/11).

🎯 Demo

(You can add a short .wav or .mp4 clip here once you test a clean interaction.)


---
