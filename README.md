# 🤖 AI Jarvis — Python AI Personal Assistant

> A Jarvis-style voice-activated AI assistant powered by **Ollama** (fully offline LLM),
> `SpeechRecognition`, and `pyttsx3`.

---

## ✨ Features

| Feature | Trigger Example |
|---|---|
| 🕒 Current time | "What's the time?" |
| 📅 Current date | "What's today's date?" |
| 🌐 Open websites | "Open YouTube" / "Open GitHub" |
| 🔎 Web search | "Search for Python tutorials" |
| 💻 Launch apps | "Open Notepad" / "Open Calculator" |
| 🎵 Play music | "Play music" / "Play song" |
| 🛑 Stop music | "Stop music" |
| 📝 Take a note | "Take a note: buy groceries" |
| 📖 Read notes | "Read my notes" |
| 🤖 AI chat (Ollama) | Any other question |
| 🔌 Exit | "Goodbye" / "Exit" / "Quit" |

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed and running

### 2. Install Ollama & Pull a Model

```bash
# Install from https://ollama.com/download
# Then pull a model (llama3 recommended):
ollama pull llama3

# Start the Ollama server (runs at http://127.0.0.1:11434 by default):
ollama serve
```

### 3. Clone & Set Up

```bash
cd AI-Jarvis

# Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure (Optional)

Copy `.env` and adjust if needed:

```bash
# .env
OLLAMA_MODEL=llama3          # change to mistral, phi3, etc.
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

### 5. Run Jarvis

```bash
python main.py
```

---

## 📁 Project Structure

```
AI-Jarvis/
├── main.py          ← Entry point, greeting & main loop
├── assistant.py     ← Command routing + Ollama LLM
├── voice.py         ← Speech recognition & TTS
├── commands.py      ← All feature handlers
├── config.py        ← Settings, allow-lists, constants
├── test_jarvis.py   ← Complete automated test suite (70+ tests)
├── requirements.txt
├── .env             ← Optional overrides (not committed)
├── .gitignore
└── README.md
```

---

## 🎵 Music Playback

Place `.mp3` files in your **`~/Music`** folder (e.g., `C:\Users\YourName\Music`).
Say _"Play music"_ and Jarvis will pick a random track.

---

## 🔧 Customisation

### Add a website
Edit `WEBSITES` in `config.py`:
```python
WEBSITES["reddit"] = "https://www.reddit.com"
```

### Add an application
Edit `APPLICATIONS` in `config.py`:
```python
APPLICATIONS["spotify"] = r"C:\Users\YourName\AppData\Roaming\Spotify\Spotify.exe"
```

### Change the AI model
```bash
ollama pull mistral
# Then in .env:
OLLAMA_MODEL=mistral
```

---

## 🔐 Security Notes

- **No API keys required** — Ollama runs 100% locally.
- Application launcher uses a strict allow-list — no raw user input ever reaches `subprocess`.
- `.env` and `notes.txt` are in `.gitignore` and never committed.

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `speechrecognition` | Microphone → text via Google STT |
| `pyttsx3` | Offline text-to-speech |
| `pygame-ce` | MP3 music playback |
| `sounddevice` | Microphone audio capture |
| `numpy` / `scipy` | Audio processing |
| `python-dotenv` | Load `.env` configuration |

---

## 🧪 Running Tests

A complete automated test suite is included. Run it without any mic, speaker, or Ollama needed:

```bash
.\venv\Scripts\python.exe test_jarvis.py
```

Expected output:
```
=================================================================
   AI Jarvis — Complete Automated Test Suite
=================================================================
test_assistant_name ... ok
test_get_time_format ... ok
...
  ALL 70+ TESTS PASSED ✓
=================================================================
```

Test coverage includes: Config · Time & Date · Web Commands · App Launcher ·
Music · Notes · Ollama integration (mocked) · Voice/keyboard fallback ·
End-to-end keyboard session · Security boundaries.

---

## 🛠️ Troubleshooting

### 🔴 Ollama / AI Chat

| Problem | Solution |
|---|---|
| *"AI model is not running"* | Open a **separate terminal** and run `ollama serve` |
| Ollama command not found | Install from [https://ollama.com](https://ollama.com) |
| Model not found (`llama3`) | Run `ollama pull llama3` first |
| Slow AI responses | Use a smaller model: `ollama pull phi3` → set `OLLAMA_MODEL=phi3` in `.env` |

---

### 🎤 Microphone / Speech Recognition

| Problem | Solution |
|---|---|
| No microphone → switches to keyboard mode | Go to **Windows Settings → Sound → Input** and set a default mic |
| *"Sorry, I didn't catch that"* repeatedly | Speak louder / closer to mic; reduce background noise |
| `[WinError 10065]` socket error | Internet is down — Google STT needs internet. Jarvis **auto-switches to keyboard mode** after 3 failures |
| STT fails despite good internet | Firewall may block Google STT — add Python to Windows Firewall exceptions |
| Mic works but recognition is poor | Set mic sample rate to **16 kHz** in Windows Sound settings |

---

### 🔊 Text-to-Speech (pyttsx3)

| Problem | Solution |
|---|---|
| No voice output | Check **Settings → Time & Language → Speech → Voice** on Windows |
| Wrong voice gender | Edit the voice selector loop in `voice.py` to match your installed voice name |
| `pyttsx3` crashes on startup | Reinstall: `pip install --upgrade pyttsx3` |
| Voice not working on Linux | Install espeak: `sudo apt install espeak` |

---

### 🎵 Music Playback

| Problem | Solution |
|---|---|
| *"No MP3 files found"* | Add `.mp3` files to `C:\Users\YourName\Music` |
| *"Music folder not found"* | Create the `Music` folder in your home directory |
| Music plays but no sound | Check system volume; verify `pygame.mixer` initialised (check console logs) |
| `pygame.mixer` init fails | Reinstall: `pip install pygame-ce --upgrade` |

---

### 💻 Application Launcher

| Problem | Solution |
|---|---|
| *"Couldn't find [app] at expected path"* | App not installed at default path — update `APPLICATIONS` in `config.py` |
| VS Code not opening | Check the path in `config.py` matches your VS Code install location |
| Chrome / Firefox not found | Update the path in `APPLICATIONS` dict in `config.py` |

---

### ⚙️ General / Setup

| Problem | Solution |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside the activated `venv` |
| `venv\Scripts\python.exe` not found | Create venv first: `python -m venv venv` |
| Unicode/emoji errors on Windows terminal | Run `chcp 65001` in terminal before starting Jarvis |
| Tests fail with import errors | Run tests from inside the `AI-Jarvis/` directory |
