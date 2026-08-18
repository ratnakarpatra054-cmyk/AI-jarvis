"""
voice.py — Speech Recognition & Text-to-Speech for AI Jarvis

Uses sounddevice (pre-built wheel for Python 3.14) instead of PyAudio
for microphone capture, then passes audio to SpeechRecognition for STT.
Falls back to keyboard input if no microphone is found OR if the network
is unavailable for Google STT.
"""

import io
import logging
import time
import wave

import speech_recognition as sr
import pyttsx3

from config import TTS_RATE, TTS_VOLUME, LISTEN_TIMEOUT, PHRASE_LIMIT, ASSISTANT_NAME

logger = logging.getLogger(__name__)

# ─── TTS Engine (initialised once) ───────────────────────────────────────────
_engine = pyttsx3.init()
_engine.setProperty("rate",   TTS_RATE)
_engine.setProperty("volume", TTS_VOLUME)

# Try to select a female/Zira voice
_voices = _engine.getProperty("voices")
for _v in _voices:
    if "female" in _v.name.lower() or "zira" in _v.name.lower():
        _engine.setProperty("voice", _v.id)
        break

# ─── Sounddevice availability check ──────────────────────────────────────────
_SD_AVAILABLE = False
_sd = None
_np = None

try:
    import sounddevice as _sd_mod
    import numpy as _np_mod
    # Quick sanity-check: query device list (raises if PortAudio missing)
    _sd_mod.query_devices()
    _sd = _sd_mod
    _np = _np_mod
    _SD_AVAILABLE = True
except Exception as exc:
    logger.warning("sounddevice unavailable (%s) — running in KEYBOARD MODE.", exc)

if not _SD_AVAILABLE:
    print(
        "\n[WARN] Microphone access unavailable — running in KEYBOARD MODE.\n"
        "       Type your commands below. Voice input is disabled.\n"
        "       To enable voice: install Microsoft C++ Build Tools from\n"
        "       https://visualstudio.microsoft.com/visual-cpp-build-tools/\n"
        "       then run: pip install pyaudio\n"
    )

# ─── Network error tracking (auto-switch to keyboard on STT failures) ─────────
_STT_FAIL_LIMIT   = 3      # consecutive network failures before switching to keyboard
_stt_fail_count   = 0      # running tally
_keyboard_fallback = False  # set True when network is down


def speak(text: str) -> None:
    """Convert text to speech and print to console."""
    # Security: only assistant-generated text is spoken — no raw user input echoed
    print(f"[{ASSISTANT_NAME}]: {text}")
    try:
        _engine.say(text)
        _engine.runAndWait()
    except Exception as exc:
        logger.warning("TTS error: %s", exc)


def listen() -> str | None:
    """
    Listen via microphone (sounddevice) or keyboard fallback.
    Automatically switches to keyboard mode if:
      - sounddevice is not available, OR
      - Google STT has failed too many times in a row (network down).
    Returns recognised/typed text in lowercase, or None on silence/failure.
    """
    global _keyboard_fallback

    if not _SD_AVAILABLE or _keyboard_fallback:
        return _keyboard_input()
    return _sounddevice_input()


# ─── Microphone input via sounddevice ────────────────────────────────────────

_SAMPLE_RATE = 16_000   # Hz — good quality for STT
_CHANNELS    = 1        # mono


def _sounddevice_input() -> str | None:
    """
    Record audio with sounddevice, feed into SpeechRecognition.
    - On UnknownValueError (silence/noise): silent retry — returns None.
    - On RequestError (network): counts failures; auto-switches to
      keyboard mode after _STT_FAIL_LIMIT consecutive errors.
    - On any other exception: logs and returns None.
    """
    global _stt_fail_count, _keyboard_fallback

    print(f"\n[Listening...] (mic, speak now — up to {PHRASE_LIMIT}s)")
    try:
        # Record audio as a numpy array
        frames = _sd.rec(
            int(PHRASE_LIMIT * _SAMPLE_RATE),
            samplerate=_SAMPLE_RATE,
            channels=_CHANNELS,
            dtype="int16",
        )
        _sd.wait()   # blocks until recording is done

        # Convert numpy array to WAV bytes in memory
        wav_bytes = _numpy_to_wav(frames)

        # Hand off to SpeechRecognition
        recogniser = sr.Recognizer()
        with sr.AudioFile(wav_bytes) as source:
            audio = recogniser.record(source)

        text = recogniser.recognize_google(audio)
        print(f"[You said]: {text}")

        # Reset failure counter on success
        _stt_fail_count = 0
        return text.lower().strip()

    except sr.UnknownValueError:
        # Silence or unintelligible audio — not a network issue, don't count
        print("[Jarvis]: (couldn't hear anything — listening again...)")
        return None

    except sr.RequestError as exc:
        _stt_fail_count += 1
        logger.error("STT network error (%d/%d): %s",
                     _stt_fail_count, _STT_FAIL_LIMIT, exc)

        if _stt_fail_count >= _STT_FAIL_LIMIT:
            _keyboard_fallback = True
            speak(
                "I can't reach the speech recognition server — "
                "switching to keyboard mode. "
                "Please type your commands below."
            )
            print(
                "\n[INFO] Switched to KEYBOARD MODE due to network issues.\n"
                "       Your internet connection may be down or a firewall\n"
                "       is blocking Google Speech Recognition.\n"
                "       Type your commands at the prompt below.\n"
            )
        else:
            speak(
                "I'm having trouble connecting to speech recognition. "
                f"Retrying... ({_STT_FAIL_LIMIT - _stt_fail_count} attempts left)"
            )
        return None

    except Exception as exc:
        logger.error("Microphone recording error: %s", exc)
        speak("Something went wrong with the microphone.")
        return None


def _numpy_to_wav(frames) -> io.BytesIO:
    """Convert a int16 numpy array to an in-memory WAV file."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(_CHANNELS)
        wf.setsampwidth(2)          # int16 = 2 bytes
        wf.setframerate(_SAMPLE_RATE)
        wf.writeframes(frames.tobytes())
    buf.seek(0)
    return buf


# ─── Keyboard fallback ────────────────────────────────────────────────────────

def _keyboard_input() -> str | None:
    """Read a command from stdin when microphone/network is unavailable."""
    try:
        text = input("\n[Type command] > ").strip()
        return text.lower() if text else None
    except (EOFError, KeyboardInterrupt):
        return "exit"
