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
├── main.py         ← Entry point, greeting & main loop
├── assistant.py    ← Command routing + Ollama LLM
├── voice.py        ← Speech recognition & TTS
├── commands.py     ← All feature handlers
├── config.py       ← Settings, allow-lists, constants
├── requirements.txt
├── .env            ← Optional overrides (not committed)
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
| `pygame` | MP3 music playback |
| `python-dotenv` | Load `.env` configuration |
| `requests` | HTTP utilities (optional use) |

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---|---|
| "Ollama not reachable" | Run `ollama serve` in a separate terminal |
| No microphone detected | Check Windows Sound Settings → Input devices |
| "No MP3 files found" | Add `.mp3` files to `~/Music` |
| pyttsx3 voice not working | Install `espeak` (Linux) or use Windows built-in voices |
