"""
main.py — Entry Point for AI Jarvis
Greets the user and runs the main voice-command loop.
"""

import datetime
import logging
import sys
import io

# Force UTF-8 output so emoji / unicode prints correctly on Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Configure logging — output to console, no sensitive data ever logged
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("main")

from config import ASSISTANT_NAME
from voice import speak, listen
from assistant import process_command


def get_greeting() -> str:
    """Return a time-appropriate greeting."""
    hour = datetime.datetime.now().hour
    if hour < 12:
        period = "morning"
    elif hour < 17:
        period = "afternoon"
    else:
        period = "evening"
    return f"Good {period}! I'm {ASSISTANT_NAME}, your AI assistant. How can I help you?"


def main() -> None:
    print("=" * 55)
    print(f"  [AI]  {ASSISTANT_NAME} - AI Personal Assistant")
    print("=" * 55)

    speak(get_greeting())

    while True:
        try:
            text = listen()

            if text is None:
                # No speech detected — keep looping silently
                continue

            response = process_command(text)

            if response == "__EXIT__":
                speak(f"Goodbye! Have a great day.")
                break

            if response:
                speak(response)

        except KeyboardInterrupt:
            speak("Shutting down. Goodbye!")
            logger.info("Jarvis shut down via KeyboardInterrupt.")
            break
        except Exception as exc:
            # Catch-all: generic message to user, detailed log for developer
            logger.exception("Unexpected error in main loop: %s", exc)
            speak("Something went wrong on my end. Please try again.")


if __name__ == "__main__":
    main()
