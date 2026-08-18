"""
config.py — Configuration & Constants for AI Jarvis
Loads secrets from .env (if present) and exposes runtime settings.
"""

import os
import pathlib
from dotenv import load_dotenv

# ─── Load .env (if present) ──────────────────────────────────────────────────
load_dotenv()

# ─── Assistant Identity ───────────────────────────────────────────────────────
ASSISTANT_NAME = "Jarvis"
WAKE_WORD      = "jarvis"        # lowercase keyword to activate

# ─── Ollama Settings (local LLM — no API key required) ───────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "llama3")   # change to any pulled model

# ─── File Paths ───────────────────────────────────────────────────────────────
BASE_DIR    = pathlib.Path(__file__).parent.resolve()
NOTES_FILE  = BASE_DIR / "notes.txt"
MUSIC_FOLDER = pathlib.Path.home() / "Music"   # ~/Music — user's music directory

# ─── Allowed Websites (for "open <name>" command) ────────────────────────────
WEBSITES: dict[str, str] = {
    "google"        : "https://www.google.com",
    "youtube"       : "https://www.youtube.com",
    "github"        : "https://www.github.com",
    "stackoverflow" : "https://stackoverflow.com",
    "wikipedia"     : "https://www.wikipedia.org",
    "gmail"         : "https://mail.google.com",
    "maps"          : "https://maps.google.com",
    "chatgpt"       : "https://chat.openai.com",
    "linkedin"      : "https://www.linkedin.com",
    "whatsapp"      : "https://web.whatsapp.com",
    "twitter"       : "https://www.twitter.com",
    "instagram"     : "https://www.instagram.com",
    "netflix"       : "https://www.netflix.com",
    "reddit"        : "https://www.reddit.com",
    "amazon"        : "https://www.amazon.in",
    "flipkart"      : "https://www.flipkart.com",
}

# ─── Allowed Applications (hardcoded allow-list — no user input reaches shell) ─
# Security: user speech is matched against THIS dict only; no raw input passed to subprocess.
APPLICATIONS: dict[str, str] = {
    "notepad"     : "notepad.exe",
    "calculator"  : "calc.exe",
    "paint"       : "mspaint.exe",
    "explorer"    : "explorer.exe",
    "word"        : "WINWORD.EXE",
    "excel"       : "EXCEL.EXE",
    "powerpoint"  : "POWERPNT.EXE",
    "chrome"      : r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox"     : r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "vs code"     : r"C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe".format(os.getlogin()),
    "terminal"    : "cmd.exe",
    "task manager": "taskmgr.exe",
    "edge"        : r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "spotify"     : r"C:\Users\{}\AppData\Roaming\Spotify\Spotify.exe".format(os.getlogin()),
    "whatsapp"    : r"C:\Users\{}\AppData\Local\WhatsApp\WhatsApp.exe".format(os.getlogin()),
    "vlc"         : r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    "snipping tool": "SnippingTool.exe",
    "settings"    : "ms-settings:",
}

# ─── TTS Settings ─────────────────────────────────────────────────────────────
TTS_RATE   = 175     # words per minute
TTS_VOLUME = 0.9     # 0.0 – 1.0

# ─── Speech Recognition ───────────────────────────────────────────────────────
LISTEN_TIMEOUT  = 5   # seconds to wait for phrase start
PHRASE_LIMIT    = 10  # max seconds per phrase
