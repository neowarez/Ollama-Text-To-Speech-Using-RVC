# ollama_tts.py

import os
import json
import subprocess
import winsound
import requests
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# ==========================
# ✅ Paths
# ==========================
PIPER_MODEL = r"C:\piper\models\en_US-amy-medium.onnx"  # neutral base voice
PIPER_EXE = r"C:\piper\piper.exe"
OUTPUT_FILE = r"C:\piper\reply.wav"

# ✅ RVC model (just filename, not full path)
RVC_MODEL_NAME = "PrincessBubblegumv1_best.pth"
RVC_INDEX = r"D:\RVC\RVC1006AMD_Intel\models\PrincessBubblegumv1.index"
RVC_SCRIPT = r"D:\RVC\Retrieval-based-Voice-Conversion-WebUI\tools\infer_cli.py"
RVC_ROOT = os.path.dirname(os.path.dirname(RVC_SCRIPT))  # one level up from tools/


# ✅ Force RVC to run with venv310 Python
PYTHON_EXE = r"C:\ollamatts\venv310\Scripts\python.exe"

# ✅ Ollama model
MODEL_NAME = "moondream"
BOT_NAME = MODEL_NAME

# ✅ Vosk STT model
VOSK_MODEL_PATH = r"D:\vosk-model-small-en-us-0.15"
if not os.path.exists(VOSK_MODEL_PATH):
    raise FileNotFoundError(f"❌ Vosk model not found at {VOSK_MODEL_PATH}")
model = Model(VOSK_MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)


# ==========================
# 🔄 RVC voice conversion (with audio fixing)
# ==========================
# ==========================
# 🔄 RVC voice conversion (with audio fixing)
# ==========================
def convert_with_rvc(input_wav, output_wav):
    """Convert Piper's TTS output into your trained RVC voice."""
    try:
        # Step 1: Preprocess with ffmpeg
        fixed_input = input_wav.replace(".wav", "_clean.wav")
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-i", input_wav,
            "-ar", "44100", "-ac", "1", "-acodec", "pcm_s16le",
            fixed_input
        ]
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"🔧 Preprocessed audio saved: {fixed_input}")

        # Step 2: Run RVC with venv’s python
        subprocess.run(
    [
        PYTHON_EXE, RVC_SCRIPT,
        "--model_name", RVC_MODEL_NAME,   # 👈 only filename
        "--index_path", RVC_INDEX,
        "--input_path", fixed_input,
        "--opt_path", output_wav,
        "--f0method", "rmvpe",
        "--device", "cpu"
    ],
    cwd=RVC_ROOT,   # 👈 so assets/weights works
    check=True
)

        print(f"🎙️ RVC conversion complete: {output_wav}")
        return output_wav

    except Exception as e:
        print(f"❌ RVC conversion error: {e}")
        return input_wav  # fallback


# ==========================
# 🗣️ Piper + RVC TTS
# ==========================
def speak_with_piper(text: str):
    """Generate Piper TTS → Fix audio → Convert with RVC → Play final audio"""
    try:
        # Step 1: Piper output
        subprocess.run(
            [PIPER_EXE, "--model", PIPER_MODEL, "--output_file", OUTPUT_FILE],
            input=text.encode("utf-8"),
            check=True
        )

        # Step 2: RVC conversion
        rvc_out = OUTPUT_FILE.replace(".wav", "_rvc.wav")
        final_audio = convert_with_rvc(OUTPUT_FILE, rvc_out)

        # Step 3: Play final result
        winsound.PlaySound(final_audio, winsound.SND_FILENAME)

    except Exception as e:
        print(f"❌ Piper+RVC error: {e}")


# ==========================
# 🎤 Offline STT (Vosk)
# ==========================
def listen_to_user():
    """Capture speech from mic and convert to text"""
    print("\n🎤 Speak now...")
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1) as stream:
        while True:
            data, _ = stream.read(4000)
            if recognizer.AcceptWaveform(bytes(data)):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    print(f"You (speech): {text}")
                    return text.lower()


# ==========================
# 🧠 Stream response from Ollama
# ==========================
def stream_ollama(prompt: str):
    """Send a prompt to Ollama and stream back response with TTS"""
    print(f"{BOT_NAME}: ", end="", flush=True)
    buffer = ""

    try:
        with requests.post(
            "http://localhost:11434/api/generate",
            json={"model": MODEL_NAME, "prompt": prompt, "stream": True},
            stream=True,
        ) as resp:
            for line in resp.iter_lines():
                if not line:
                    continue
                data = json.loads(line.decode("utf-8"))
                if "response" in data:
                    token = data["response"]
                    buffer += token
                    print(token, end="", flush=True)

                    # Speak sentence by sentence
                    if token in [".", "!", "?"]:
                        chunk = buffer.strip()
                        if chunk:
                            speak_with_piper(chunk)
                            buffer = ""

                if data.get("done", False):
                    break

            if buffer.strip():
                speak_with_piper(buffer.strip())
        print()
    except Exception as e:
        print(f"❌ Ollama request error: {e}")


# ==========================
# 🔄 Main loop
# ==========================
if __name__ == "__main__":
    voice_control_enabled = False

    while True:
        try:
            if voice_control_enabled:
                user_input = listen_to_user()
                if not user_input:
                    continue

                if "disable voice control" in user_input:
                    print("🛑 Voice control disabled.")
                    voice_control_enabled = False
                    continue

                stream_ollama(user_input)

            else:
                choice = input("\nType a message (/bye to quit): ").strip()
                if choice.lower() == "/bye":
                    print("👋 Goodbye!")
                    break
                elif choice.lower() == "activate voice control":
                    print("🎤 Voice control enabled! Speak freely.")
                    voice_control_enabled = True
                else:
                    stream_ollama(choice)

        except KeyboardInterrupt:
            print("\n👋 Exiting.")
            break
