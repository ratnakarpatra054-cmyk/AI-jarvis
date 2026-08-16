"""
assistant.py — Core Orchestration Logic for AI Jarvis
Routes recognised speech to the correct handler or Ollama LLM fallback.
"""

import json
import logging
import urllib.request
import urllib.error

from config import OLLAMA_BASE_URL, OLLAMA_MODEL, ASSISTANT_NAME
from commands import (
    get_time, get_date,
    open_website, web_search,
    open_application,
    play_music, stop_music,
    take_note, read_notes,
)

logger = logging.getLogger(__name__)


# ─── Ollama LLM ──────────────────────────────────────────────────────────────

def ask_ollama(prompt: str) -> str:
    """
    Send a prompt to a locally running Ollama instance (http://127.0.0.1:11434).
    Returns the model's reply as a string.
    Security:
      - Communicates only with localhost — no external network calls.
      - Request body is JSON-serialised (no injection risk).
      - Response is validated as JSON before use.
    """
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,          # single-shot response for simplicity
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310 — localhost only
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "").strip()
    except urllib.error.URLError:
        return (
            "The local AI model is not running. "
            "To enable AI chat, install Ollama from ollama dot com, "
            f"then run: ollama pull {OLLAMA_MODEL}, and ollama serve. "
            "All other Jarvis features are working fine."
        )
    except (json.JSONDecodeError, KeyError) as exc:
        logger.error("Unexpected Ollama response format: %s", exc)
        return "I received an unexpected response from the AI model."


# ─── Command Router ───────────────────────────────────────────────────────────

def process_command(text: str) -> str:
    """
    Parse the spoken text and route to the correct handler.
    Returns a response string to be spoken back to the user.
    """
    if not text:
        return ""

    # ── Time & Date ──
    if "time" in text:
        return get_time()
    if "date" in text or "day" in text:
        return get_date()

    # ── Music ──
    if "stop music" in text or "pause music" in text:
        return stop_music()
    if "play music" in text or "play song" in text or "play some music" in text:
        return play_music(text)

    # ── Notes ──
    if any(kw in text for kw in ("take a note", "make a note", "note down", "note that", "write note")):
        return take_note(text)
    if "read notes" in text or "read my notes" in text or "show notes" in text:
        return read_notes()

    # ── Open website ──
    if "open" in text and any(site in text for site in ("google", "youtube", "github",
                                                          "stackoverflow", "wikipedia",
                                                          "gmail", "maps", "chatgpt")):
        return open_website(text)

    # ── Web search ──
    if any(kw in text for kw in ("search for", "search", "look up", "google")):
        return web_search(text)

    # ── Application launcher ──
    if "open" in text:
        result = open_application(text)
        if "don't have that application" not in result:
            return result

    # ── Exit ──
    if any(kw in text for kw in ("exit", "quit", "goodbye", "bye", "shutdown", "stop jarvis")):
        return "__EXIT__"

    # ── Fallback: Ollama AI ──
    return ask_ollama(text)
