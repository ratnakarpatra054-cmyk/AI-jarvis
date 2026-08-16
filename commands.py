"""
commands.py — Command Handlers for AI Jarvis
Each public function handles one category of command and returns a response string.
"""

import os
import re
import random
import logging
import subprocess
import webbrowser
import datetime
import pathlib
from typing import Optional

import pygame

from config import WEBSITES, APPLICATIONS, NOTES_FILE, MUSIC_FOLDER

logger = logging.getLogger(__name__)

# ─── Pygame mixer (initialised once for music) ───────────────────────────────
try:
    pygame.mixer.init()
    _PYGAME_READY = True
except Exception as exc:                                # pragma: no cover
    logger.warning("pygame.mixer could not initialise: %s", exc)
    _PYGAME_READY = False


# ─── Time & Date ─────────────────────────────────────────────────────────────

def get_time() -> str:
    now = datetime.datetime.now()
    return f"The current time is {now.strftime('%I:%M %p')}."


def get_date() -> str:
    today = datetime.date.today()
    return f"Today is {today.strftime('%A, %B %d, %Y')}."


# ─── Web / Browser ───────────────────────────────────────────────────────────

def open_website(command: str) -> str:
    """
    Match spoken site name against the allow-list in WEBSITES.
    Security: only pre-approved URLs are ever opened.
    """
    for name, url in WEBSITES.items():
        if name in command:
            webbrowser.open(url)
            return f"Opening {name} for you."
    return "I don't have that website saved. Say 'open google' or 'open youtube'."


def web_search(command: str) -> str:
    """
    Extract query after 'search' or 'look up' keyword and open Google.
    Security: query is URL-encoded by webbrowser.open via urllib inside Google's URL.
    """
    query = _extract_after(command, ("search for", "search", "look up", "google"))
    if not query:
        return "What would you like me to search for?"
    import urllib.parse
    safe_query = urllib.parse.quote_plus(query)
    webbrowser.open(f"https://www.google.com/search?q={safe_query}")
    return f"Searching Google for: {query}"


# ─── Application Launcher ────────────────────────────────────────────────────

def open_application(command: str) -> str:
    """
    Match spoken app name against the hardcoded APPLICATIONS allow-list.
    Security: No user-controlled string is passed to subprocess — only
    the allow-list value is used as the executable path.
    """
    for name, exe in APPLICATIONS.items():
        if name in command:
            exe_path = pathlib.Path(exe)
            # Verify the executable actually exists (where it has an absolute path)
            if exe_path.is_absolute() and not exe_path.exists():
                return f"I couldn't find {name} at the expected path."
            try:
                subprocess.Popen(  # noqa: S603 — allow-list only, no user input
                    [str(exe_path)],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return f"Opening {name}."
            except FileNotFoundError:
                return f"{name} is not installed or accessible on this system."
            except OSError as exc:
                logger.error("Failed to launch %s: %s", name, exc)
                return f"Sorry, I couldn't open {name}."
    return "I don't have that application on my launch list. Try 'open notepad' or 'open calculator'."


# ─── Music ───────────────────────────────────────────────────────────────────

def play_music(command: str) -> str:
    """
    Play a random .mp3 from MUSIC_FOLDER, or a specific song if named.
    Security: file path is resolved and confined within MUSIC_FOLDER.
    """
    if not _PYGAME_READY:
        return "Music playback is unavailable — pygame could not initialise."

    if not MUSIC_FOLDER.exists():
        return (
            f"Music folder not found at {MUSIC_FOLDER}. "
            "Please add .mp3 files there."
        )

    songs = list(MUSIC_FOLDER.glob("*.mp3"))
    if not songs:
        return "No MP3 files found in your Music folder."

    # Try to match a song name from the command
    chosen: Optional[pathlib.Path] = None
    for song in songs:
        if song.stem.lower() in command:
            chosen = song
            break

    chosen = chosen or random.choice(songs)

    # Security: resolve path and confirm it stays within MUSIC_FOLDER
    resolved = chosen.resolve()
    if not str(resolved).startswith(str(MUSIC_FOLDER.resolve())):
        logger.warning("Path traversal attempt blocked: %s", resolved)
        return "I can't play that file."

    pygame.mixer.music.load(str(resolved))
    pygame.mixer.music.play()
    return f"Playing {chosen.stem}."


def stop_music() -> str:
    if _PYGAME_READY and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        return "Music stopped."
    return "Nothing is playing right now."


# ─── Notes ───────────────────────────────────────────────────────────────────

def take_note(command: str) -> str:
    """
    Save a note to notes.txt.
    Security: file path is fixed via config — not user-controlled.
    """
    note_text = _extract_after(command, ("take a note", "make a note", "note down", "note that", "write"))
    if not note_text:
        return "What would you like me to note?"

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"[{timestamp}] {note_text}\n"

    try:
        with open(NOTES_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
        return f"Note saved: {note_text}"
    except OSError as exc:
        logger.error("Failed to write note: %s", exc)
        return "I couldn't save the note. Please check file permissions."


def read_notes() -> str:
    """Return all saved notes as a string to be spoken."""
    try:
        if not NOTES_FILE.exists():
            return "You have no notes yet."
        content = NOTES_FILE.read_text(encoding="utf-8").strip()
        return content if content else "Your notes file is empty."
    except OSError as exc:
        logger.error("Failed to read notes: %s", exc)
        return "I couldn't read your notes."


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _extract_after(text: str, keywords: tuple[str, ...]) -> str:
    """Return the portion of text that follows any of the given keywords."""
    for kw in keywords:
        idx = text.find(kw)
        if idx != -1:
            remainder = text[idx + len(kw):].strip()
            if remainder:
                return remainder
    return ""
