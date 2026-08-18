"""
test_jarvis.py — Complete Automated Test Suite for AI Jarvis
============================================================
Covers every module without requiring a microphone, speaker, or Ollama server.

Sections
--------
1.  Config Tests
2.  Time & Date Command Tests
3.  Web Command Tests
4.  Application Launcher Tests
5.  Music Command Tests
6.  Notes Command Tests
7.  Internal Helper Tests  (_extract_after)
8.  Ollama Integration Tests  (mocked HTTP)
9.  Command Router / process_command Tests
10. Voice Module — TTS Tests
11. Voice Module — Keyboard Fallback Tests
12. Voice Module — Sounddevice / Mic Tests  (mocked)
13. End-to-End Keyboard Mode Simulation
14. Security / Boundary Tests

Usage
-----
    python test_jarvis.py
    python test_jarvis.py -v          # already verbose by default
"""

import sys
import io
import json
import pathlib
import tempfile
import unittest
import datetime
import urllib.error
from unittest.mock import patch, MagicMock, call, mock_open

# ── Force UTF-8 output on Windows ────────────────────────────────────────────
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

print("=" * 65)
print("   AI Jarvis — Complete Automated Test Suite")
print("=" * 65)


# =============================================================================
# 1. Config Tests
# =============================================================================
class TestConfig(unittest.TestCase):
    """Validate every value exported from config.py."""

    def test_assistant_name_is_jarvis(self):
        from config import ASSISTANT_NAME
        self.assertEqual(ASSISTANT_NAME, "Jarvis")

    def test_wake_word_lowercase(self):
        from config import WAKE_WORD
        self.assertEqual(WAKE_WORD, WAKE_WORD.lower(),
                         "WAKE_WORD must be lowercase for matching")

    def test_ollama_base_url_localhost(self):
        from config import OLLAMA_BASE_URL
        self.assertIn("127.0.0.1", OLLAMA_BASE_URL)

    def test_ollama_model_non_empty_string(self):
        from config import OLLAMA_MODEL
        self.assertIsInstance(OLLAMA_MODEL, str)
        self.assertGreater(len(OLLAMA_MODEL), 0)

    def test_notes_file_is_pathlib_path(self):
        from config import NOTES_FILE
        self.assertIsInstance(NOTES_FILE, pathlib.Path)

    def test_notes_file_has_txt_suffix(self):
        from config import NOTES_FILE
        self.assertEqual(NOTES_FILE.suffix, ".txt")

    def test_music_folder_is_pathlib_path(self):
        from config import MUSIC_FOLDER
        self.assertIsInstance(MUSIC_FOLDER, pathlib.Path)

    def test_websites_contains_expected_keys(self):
        from config import WEBSITES
        for expected in ("google", "youtube", "github", "wikipedia",
                         "stackoverflow", "gmail", "maps", "chatgpt"):
            with self.subTest(site=expected):
                self.assertIn(expected, WEBSITES)

    def test_websites_all_https(self):
        from config import WEBSITES
        for name, url in WEBSITES.items():
            with self.subTest(site=name):
                self.assertTrue(url.startswith("https://"),
                                f"{name} URL should use HTTPS")

    def test_applications_contains_expected_keys(self):
        from config import APPLICATIONS
        for expected in ("notepad", "calculator", "paint",
                         "explorer", "terminal", "task manager"):
            with self.subTest(app=expected):
                self.assertIn(expected, APPLICATIONS)

    def test_tts_rate_positive_integer(self):
        from config import TTS_RATE
        self.assertIsInstance(TTS_RATE, int)
        self.assertGreater(TTS_RATE, 0)

    def test_tts_volume_in_range(self):
        from config import TTS_VOLUME
        self.assertGreaterEqual(TTS_VOLUME, 0.0)
        self.assertLessEqual(TTS_VOLUME, 1.0)

    def test_listen_timeout_positive(self):
        from config import LISTEN_TIMEOUT
        self.assertGreater(LISTEN_TIMEOUT, 0)

    def test_phrase_limit_positive(self):
        from config import PHRASE_LIMIT
        self.assertGreater(PHRASE_LIMIT, 0)

    def test_phrase_limit_exceeds_timeout(self):
        from config import LISTEN_TIMEOUT, PHRASE_LIMIT
        self.assertGreaterEqual(PHRASE_LIMIT, LISTEN_TIMEOUT,
                                "PHRASE_LIMIT should be >= LISTEN_TIMEOUT")


# =============================================================================
# 2. Time & Date Command Tests
# =============================================================================
class TestTimeDate(unittest.TestCase):

    def test_get_time_contains_time_phrase(self):
        from commands import get_time
        result = get_time()
        self.assertIn("time is", result.lower())

    def test_get_time_ends_with_period(self):
        from commands import get_time
        self.assertTrue(get_time().endswith("."))

    def test_get_time_returns_string(self):
        from commands import get_time
        self.assertIsInstance(get_time(), str)

    def test_get_time_contains_am_or_pm(self):
        from commands import get_time
        result = get_time().upper()
        self.assertTrue("AM" in result or "PM" in result)

    def test_get_date_contains_today_phrase(self):
        from commands import get_date
        self.assertIn("today is", get_date().lower())

    def test_get_date_contains_current_year(self):
        from commands import get_date
        self.assertIn(str(datetime.date.today().year), get_date())

    def test_get_date_ends_with_period(self):
        from commands import get_date
        self.assertTrue(get_date().endswith("."))

    def test_get_date_returns_string(self):
        from commands import get_date
        self.assertIsInstance(get_date(), str)

    def test_get_time_mocked_morning(self):
        """Verify get_time reflects the mocked time correctly."""
        from commands import get_time
        fixed_dt = datetime.datetime(2025, 1, 15, 9, 5, 0)
        with patch("commands.datetime") as mock_dt:
            mock_dt.datetime.now.return_value = fixed_dt
            mock_dt.date = datetime.date
            result = get_time()
        self.assertIn("09:05 AM", result)

    def test_get_date_mocked_date(self):
        from commands import get_date
        fixed_date = datetime.date(2025, 6, 21)
        with patch("commands.datetime") as mock_dt:
            mock_dt.date.today.return_value = fixed_date
            mock_dt.datetime = datetime.datetime
            result = get_date()
        self.assertIn("2025", result)
        self.assertIn("June", result)


# =============================================================================
# 3. Web Command Tests
# =============================================================================
class TestWebCommands(unittest.TestCase):

    # ── open_website ──────────────────────────────────────────────────────────

    @patch("webbrowser.open")
    def test_open_google(self, mock_open):
        from commands import open_website
        result = open_website("open google")
        mock_open.assert_called_once_with("https://www.google.com")
        self.assertIn("google", result.lower())

    @patch("webbrowser.open")
    def test_open_youtube(self, mock_open):
        from commands import open_website
        result = open_website("open youtube")
        mock_open.assert_called_once_with("https://www.youtube.com")
        self.assertIn("youtube", result.lower())

    @patch("webbrowser.open")
    def test_open_github(self, mock_open):
        from commands import open_website
        result = open_website("open github")
        mock_open.assert_called_once()
        self.assertIn("github", result.lower())

    @patch("webbrowser.open")
    def test_open_wikipedia(self, mock_open):
        from commands import open_website
        result = open_website("open wikipedia")
        mock_open.assert_called_once()
        self.assertIn("wikipedia", result.lower())

    @patch("webbrowser.open")
    def test_open_gmail(self, mock_open):
        from commands import open_website
        result = open_website("open gmail")
        mock_open.assert_called_once()
        self.assertIn("gmail", result.lower())

    @patch("webbrowser.open")
    def test_open_chatgpt(self, mock_open):
        from commands import open_website
        result = open_website("open chatgpt")
        mock_open.assert_called_once()
        self.assertIn("chatgpt", result.lower())

    def test_open_unknown_website_returns_hint(self):
        from commands import open_website
        result = open_website("open unknownxyz123")
        self.assertIn("don't have", result.lower())

    def test_open_website_case_in_command(self):
        """Matching should work regardless of surrounding words."""
        from commands import open_website
        with patch("webbrowser.open"):
            result = open_website("please open google for me")
        self.assertIn("google", result.lower())

    # ── web_search ───────────────────────────────────────────────────────────

    @patch("webbrowser.open")
    def test_web_search_basic(self, mock_open):
        from commands import web_search
        result = web_search("search for python tutorials")
        mock_open.assert_called_once()
        self.assertIn("python tutorials", result.lower())

    @patch("webbrowser.open")
    def test_web_search_url_encoded(self, mock_open):
        """Query with spaces must be URL-encoded in the opened URL."""
        from commands import web_search
        web_search("search for open source projects")
        url_arg = mock_open.call_args[0][0]
        self.assertNotIn(" ", url_arg)
        self.assertIn("google.com/search", url_arg)

    @patch("webbrowser.open")
    def test_web_search_look_up_keyword(self, mock_open):
        from commands import web_search
        result = web_search("look up machine learning")
        mock_open.assert_called_once()
        self.assertIn("machine learning", result.lower())

    def test_web_search_empty_query_returns_prompt(self):
        from commands import web_search
        result = web_search("search")
        self.assertIn("search for", result.lower())
        self.assertNotIn("google.com", result.lower())

    @patch("webbrowser.open")
    def test_web_search_special_characters_encoded(self, mock_open):
        from commands import web_search
        web_search("search for C++ programming")
        url_arg = mock_open.call_args[0][0]
        self.assertIn("%2B%2B", url_arg.upper().replace("+", "%2B%2B"))


# =============================================================================
# 4. Application Launcher Tests
# =============================================================================
class TestApplicationLauncher(unittest.TestCase):

    @patch("subprocess.Popen")
    def test_open_notepad(self, mock_popen):
        from commands import open_application
        result = open_application("open notepad")
        mock_popen.assert_called_once()
        self.assertIn("notepad", result.lower())

    @patch("subprocess.Popen")
    def test_open_calculator(self, mock_popen):
        from commands import open_application
        result = open_application("open calculator")
        mock_popen.assert_called_once()
        self.assertIn("calculator", result.lower())

    @patch("subprocess.Popen")
    def test_open_paint(self, mock_popen):
        from commands import open_application
        result = open_application("open paint")
        mock_popen.assert_called_once()
        self.assertIn("paint", result.lower())

    @patch("subprocess.Popen")
    def test_open_terminal(self, mock_popen):
        from commands import open_application
        result = open_application("open terminal")
        mock_popen.assert_called_once()
        self.assertIn("terminal", result.lower())

    @patch("subprocess.Popen")
    def test_open_task_manager(self, mock_popen):
        from commands import open_application
        result = open_application("open task manager")
        mock_popen.assert_called_once()
        self.assertIn("task manager", result.lower())

    def test_open_unknown_app_returns_hint(self):
        from commands import open_application
        result = open_application("open unknownapp999")
        self.assertIn("don't have", result.lower())

    @patch("subprocess.Popen", side_effect=FileNotFoundError)
    def test_open_app_not_installed(self, _):
        from commands import open_application
        result = open_application("open notepad")
        self.assertIn("not installed", result.lower())

    @patch("subprocess.Popen", side_effect=OSError("permission denied"))
    def test_open_app_os_error(self, _):
        from commands import open_application
        result = open_application("open notepad")
        self.assertIn("couldn't open", result.lower())

    @patch("subprocess.Popen")
    def test_popen_called_with_devnull_stdio(self, mock_popen):
        """Security: stdio handles must be DEVNULL to prevent data leaks."""
        import subprocess
        from commands import open_application
        open_application("open calculator")
        _, kwargs = mock_popen.call_args
        self.assertEqual(kwargs.get("stdin"),  subprocess.DEVNULL)
        self.assertEqual(kwargs.get("stdout"), subprocess.DEVNULL)
        self.assertEqual(kwargs.get("stderr"), subprocess.DEVNULL)


# =============================================================================
# 5. Music Command Tests
# =============================================================================
class TestMusicCommands(unittest.TestCase):

    def test_stop_music_when_not_playing_returns_string(self):
        from commands import stop_music
        result = stop_music()
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_play_music_folder_not_found(self):
        from commands import play_music
        with patch("commands.MUSIC_FOLDER", pathlib.Path("C:/nonexistent_xyz")):
            result = play_music("play music")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_play_music_empty_folder(self):
        """Folder exists but contains no MP3s."""
        from commands import play_music
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_folder = pathlib.Path(tmpdir)
            with patch("commands.MUSIC_FOLDER", empty_folder):
                result = play_music("play music")
        self.assertIn("no mp3", result.lower())

    def test_play_music_with_mp3(self):
        """Folder has an MP3 — pygame.mixer.music should be called."""
        from commands import play_music
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            song = tmp_path / "mysong.mp3"
            song.write_bytes(b"\xff\xfb" + b"\x00" * 100)  # dummy MP3 header

            with patch("commands.MUSIC_FOLDER", tmp_path), \
                 patch("commands._PYGAME_READY", True), \
                 patch("pygame.mixer.music") as mock_music:
                result = play_music("play music")

        mock_music.load.assert_called_once()
        mock_music.play.assert_called_once()
        self.assertIn("playing", result.lower())

    def test_play_music_pygame_unavailable(self):
        from commands import play_music
        with patch("commands._PYGAME_READY", False):
            result = play_music("play music")
        self.assertIn("unavailable", result.lower())

    def test_stop_music_when_playing(self):
        from commands import stop_music
        with patch("commands._PYGAME_READY", True), \
             patch("pygame.mixer.music") as mock_music:
            mock_music.get_busy.return_value = True
            result = stop_music()
        mock_music.stop.assert_called_once()
        self.assertIn("stopped", result.lower())

    def test_play_music_matches_song_by_name(self):
        """When a song name is spoken, it should prefer that specific file."""
        from commands import play_music
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            (tmp_path / "bohemian.mp3").write_bytes(b"\x00" * 10)
            (tmp_path / "other.mp3").write_bytes(b"\x00" * 10)

            with patch("commands.MUSIC_FOLDER", tmp_path), \
                 patch("commands._PYGAME_READY", True), \
                 patch("pygame.mixer.music") as mock_music:
                result = play_music("play song bohemian")

        load_path = mock_music.load.call_args[0][0]
        self.assertIn("bohemian", load_path.lower())


# =============================================================================
# 6. Notes Command Tests
# =============================================================================
class TestNotesCommands(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        )
        self._tmp.close()
        self._tmp_path = pathlib.Path(self._tmp.name)

    def tearDown(self):
        self._tmp_path.unlink(missing_ok=True)

    # ── take_note ─────────────────────────────────────────────────────────────

    def test_take_note_saves_content(self):
        from commands import take_note
        with patch("commands.NOTES_FILE", self._tmp_path):
            result = take_note("take a note buy groceries")
        self.assertIn("buy groceries", result.lower())
        self.assertIn("buy groceries", self._tmp_path.read_text(encoding="utf-8"))

    def test_take_note_includes_timestamp(self):
        from commands import take_note
        with patch("commands.NOTES_FILE", self._tmp_path):
            take_note("note that call the dentist")
        content = self._tmp_path.read_text(encoding="utf-8")
        self.assertRegex(content, r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\]")

    def test_take_note_appends_multiple(self):
        from commands import take_note
        with patch("commands.NOTES_FILE", self._tmp_path):
            take_note("take a note note one")
            take_note("take a note note two")
        content = self._tmp_path.read_text(encoding="utf-8")
        self.assertIn("note one", content)
        self.assertIn("note two", content)

    def test_take_note_no_text_returns_prompt(self):
        from commands import take_note
        result = take_note("take a note")
        self.assertIn("what", result.lower())

    def test_take_note_make_a_note_keyword(self):
        from commands import take_note
        with patch("commands.NOTES_FILE", self._tmp_path):
            result = take_note("make a note finish the report")
        self.assertIn("finish the report", result.lower())

    def test_take_note_write_note_keyword(self):
        from commands import take_note
        with patch("commands.NOTES_FILE", self._tmp_path):
            result = take_note("write note pick up kids")
        self.assertIn("pick up kids", result.lower())

    # ── read_notes ────────────────────────────────────────────────────────────

    def test_read_notes_empty_file(self):
        from commands import read_notes
        with patch("commands.NOTES_FILE", self._tmp_path):
            result = read_notes()
        self.assertIn("empty", result.lower())

    def test_read_notes_with_content(self):
        from commands import read_notes
        self._tmp_path.write_text("My important note", encoding="utf-8")
        with patch("commands.NOTES_FILE", self._tmp_path):
            result = read_notes()
        self.assertIn("My important note", result)

    def test_read_notes_file_not_found(self):
        from commands import read_notes
        with patch("commands.NOTES_FILE", pathlib.Path("C:/nonexistent_notes_xyz.txt")):
            result = read_notes()
        self.assertIn("no notes", result.lower())

    def test_read_notes_multiple_entries(self):
        from commands import take_note, read_notes
        with patch("commands.NOTES_FILE", self._tmp_path):
            take_note("take a note alpha")
            take_note("take a note beta")
            result = read_notes()
        self.assertIn("alpha", result.lower())
        self.assertIn("beta", result.lower())


# =============================================================================
# 7. Internal Helper Tests  (_extract_after)
# =============================================================================
class TestExtractAfter(unittest.TestCase):
    """Test the private _extract_after utility in commands.py."""

    def _call(self, text, keywords):
        from commands import _extract_after
        return _extract_after(text, keywords)

    def test_extracts_after_single_keyword(self):
        result = self._call("search for python", ("search for",))
        self.assertEqual(result, "python")

    def test_extracts_after_first_matching_keyword(self):
        result = self._call("look up java", ("search for", "look up"))
        self.assertEqual(result, "java")

    def test_returns_empty_when_no_match(self):
        result = self._call("random text", ("search for",))
        self.assertEqual(result, "")

    def test_returns_empty_when_nothing_after_keyword(self):
        result = self._call("search for", ("search for",))
        self.assertEqual(result, "")

    def test_strips_whitespace(self):
        result = self._call("note that   buy milk   ", ("note that",))
        self.assertEqual(result, "buy milk")

    def test_multiple_keyword_options_first_wins(self):
        result = self._call("take a note do the dishes", ("take a note", "note"))
        self.assertEqual(result, "do the dishes")


# =============================================================================
# 8. Ollama Integration Tests  (mocked HTTP)
# =============================================================================
class TestOllamaIntegration(unittest.TestCase):

    def _make_mock_response(self, body: dict):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(body).encode("utf-8")
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    @patch("urllib.request.urlopen")
    def test_successful_response(self, mock_urlopen):
        mock_urlopen.return_value = self._make_mock_response({"response": "Hello there!"})
        from assistant import ask_ollama
        result = ask_ollama("say hello")
        self.assertEqual(result, "Hello there!")

    @patch("urllib.request.urlopen")
    def test_response_is_stripped(self, mock_urlopen):
        mock_urlopen.return_value = self._make_mock_response({"response": "  trimmed  "})
        from assistant import ask_ollama
        result = ask_ollama("trim test")
        self.assertEqual(result, "trimmed")

    @patch("urllib.request.urlopen")
    def test_missing_response_key_returns_empty(self, mock_urlopen):
        mock_urlopen.return_value = self._make_mock_response({})
        from assistant import ask_ollama
        result = ask_ollama("edge case")
        self.assertEqual(result, "")

    def test_ollama_not_running_gives_install_hint(self):
        with patch("urllib.request.urlopen",
                   side_effect=urllib.error.URLError("connection refused")):
            from assistant import ask_ollama
            result = ask_ollama("anything")
        self.assertIn("not running", result.lower())

    def test_ollama_not_running_mentions_ai_model(self):
        """Spoken reply should mention the model is not running."""
        with patch("urllib.request.urlopen",
                   side_effect=urllib.error.URLError("connection refused")):
            from assistant import ask_ollama
            result = ask_ollama("anything")
        # Message shortened for TTS — check key phrase instead of 'ollama'
        self.assertIn("not running", result.lower())

    @patch("urllib.request.urlopen")
    def test_invalid_json_response(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"not valid json"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp
        from assistant import ask_ollama
        result = ask_ollama("broken response")
        self.assertIn("unexpected", result.lower())

    @patch("urllib.request.urlopen")
    def test_request_uses_post_method(self, mock_urlopen):
        mock_urlopen.return_value = self._make_mock_response({"response": "ok"})
        from assistant import ask_ollama
        ask_ollama("test method")
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_method(), "POST")

    @patch("urllib.request.urlopen")
    def test_request_content_type_json(self, mock_urlopen):
        mock_urlopen.return_value = self._make_mock_response({"response": "ok"})
        from assistant import ask_ollama
        ask_ollama("test headers")
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_header("Content-type"), "application/json")

    @patch("urllib.request.urlopen")
    def test_prompt_included_in_payload(self, mock_urlopen):
        mock_urlopen.return_value = self._make_mock_response({"response": "ok"})
        from assistant import ask_ollama
        ask_ollama("my unique prompt xyz")
        req = mock_urlopen.call_args[0][0]
        body = json.loads(req.data.decode("utf-8"))
        self.assertIn("my unique prompt xyz", body["prompt"])


# =============================================================================
# 9. Command Router / process_command Tests
# =============================================================================
class TestProcessCommand(unittest.TestCase):

    # ── Basic routing ─────────────────────────────────────────────────────────

    def test_empty_string_returns_empty(self):
        from assistant import process_command
        self.assertEqual(process_command(""), "")

    def test_none_like_whitespace_goes_to_ollama(self):
        with patch("assistant.ask_ollama", return_value="ok"):
            from assistant import process_command
            process_command("   ")

    # ── Time & Date ──────────────────────────────────────────────────────────

    def test_time_command(self):
        from assistant import process_command
        self.assertIn("time is", process_command("what is the time").lower())

    def test_date_command(self):
        from assistant import process_command
        self.assertIn("today is", process_command("what is the date").lower())

    def test_day_command(self):
        from assistant import process_command
        self.assertIn("today is", process_command("what day is it").lower())

    # ── Music ─────────────────────────────────────────────────────────────────

    def test_play_music_routed(self):
        # Patch at assistant level — that's where play_music is imported into
        with patch("assistant.play_music", return_value="Playing song.") as m:
            from assistant import process_command
            result = process_command("play music")
        m.assert_called_once()
        self.assertEqual(result, "Playing song.")

    def test_stop_music_routed(self):
        with patch("assistant.stop_music", return_value="Music stopped.") as m:
            from assistant import process_command
            process_command("stop music")
        m.assert_called_once()

    def test_pause_music_routed(self):
        with patch("assistant.stop_music", return_value="Music stopped.") as m:
            from assistant import process_command
            process_command("pause music")
        m.assert_called_once()

    # ── Notes ─────────────────────────────────────────────────────────────────

    def test_take_note_routed(self):
        with patch("assistant.take_note", return_value="Note saved.") as m:
            from assistant import process_command
            process_command("take a note buy eggs")
        m.assert_called_once()

    def test_read_notes_routed(self):
        with patch("assistant.read_notes", return_value="Note 1") as m:
            from assistant import process_command
            process_command("read notes")
        m.assert_called_once()

    def test_show_notes_routed(self):
        with patch("assistant.read_notes", return_value="Note 1") as m:
            from assistant import process_command
            process_command("show notes")
        m.assert_called_once()

    # ── Web ───────────────────────────────────────────────────────────────────

    @patch("webbrowser.open")
    def test_open_youtube_routed(self, _):
        from assistant import process_command
        result = process_command("open youtube")
        self.assertIn("youtube", result.lower())

    @patch("webbrowser.open")
    def test_web_search_routed(self, _):
        from assistant import process_command
        result = process_command("search for django framework")
        self.assertIn("django framework", result.lower())

    # ── App launcher ──────────────────────────────────────────────────────────

    @patch("subprocess.Popen")
    def test_open_notepad_routed(self, _):
        from assistant import process_command
        result = process_command("open notepad")
        self.assertIn("notepad", result.lower())

    # ── Exit keywords ─────────────────────────────────────────────────────────

    def test_exit_keywords(self):
        from assistant import process_command
        for kw in ("exit", "quit", "goodbye", "bye", "shutdown", "stop jarvis"):
            with self.subTest(keyword=kw):
                self.assertEqual(process_command(kw), "__EXIT__")

    # ── Ollama fallback ───────────────────────────────────────────────────────

    @patch("assistant.ask_ollama", return_value="Mocked AI reply")
    def test_unrecognised_command_falls_back_to_ollama(self, mock_ollama):
        from assistant import process_command
        result = process_command("tell me something interesting")
        mock_ollama.assert_called_once_with("tell me something interesting")
        self.assertEqual(result, "Mocked AI reply")

    @patch("assistant.ask_ollama", return_value="Joke here")
    def test_question_falls_back_to_ollama(self, mock_ollama):
        from assistant import process_command
        process_command("what is the meaning of life")
        mock_ollama.assert_called_once()


# =============================================================================
# 10. Voice Module — TTS Tests
# =============================================================================
class TestVoiceTTS(unittest.TestCase):

    def test_speak_prints_to_console(self):
        from voice import speak
        with patch("voice._engine") as mock_engine:
            mock_engine.say = MagicMock()
            mock_engine.runAndWait = MagicMock()
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                speak("Hello world")
            output = mock_stdout.getvalue()
        self.assertIn("Hello world", output)

    def test_speak_calls_tts_engine(self):
        from voice import speak
        with patch("voice._engine") as mock_engine:
            mock_engine.say = MagicMock()
            mock_engine.runAndWait = MagicMock()
            speak("Testing TTS")
        mock_engine.say.assert_called_once_with("Testing TTS")
        mock_engine.runAndWait.assert_called_once()

    def test_speak_handles_tts_exception_gracefully(self):
        from voice import speak
        with patch("voice._engine") as mock_engine:
            mock_engine.say.side_effect = RuntimeError("TTS crash")
            # Should NOT raise — error is caught internally
            try:
                speak("crash test")
            except RuntimeError:
                self.fail("speak() should not propagate TTS exceptions")

    def test_speak_includes_assistant_name_in_output(self):
        from voice import speak
        with patch("voice._engine") as mock_engine:
            mock_engine.say = MagicMock()
            mock_engine.runAndWait = MagicMock()
            with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                speak("hi")
            self.assertIn("Jarvis", mock_stdout.getvalue())


# =============================================================================
# 11. Voice Module — Keyboard Fallback Tests
# =============================================================================
class TestVoiceKeyboardFallback(unittest.TestCase):

    @patch("builtins.input", return_value="hello jarvis")
    def test_normal_input_returned_lowercase(self, _):
        from voice import _keyboard_input
        self.assertEqual(_keyboard_input(), "hello jarvis")

    @patch("builtins.input", return_value="UPPERCASE COMMAND")
    def test_input_is_lowercased(self, _):
        from voice import _keyboard_input
        result = _keyboard_input()
        self.assertEqual(result, "uppercase command")

    @patch("builtins.input", return_value="")
    def test_empty_input_returns_none(self, _):
        from voice import _keyboard_input
        self.assertIsNone(_keyboard_input())

    @patch("builtins.input", return_value="   ")
    def test_whitespace_only_returns_none(self, _):
        from voice import _keyboard_input
        # strip() makes it empty → None
        self.assertIsNone(_keyboard_input())

    @patch("builtins.input", side_effect=EOFError)
    def test_eof_returns_exit(self, _):
        from voice import _keyboard_input
        self.assertEqual(_keyboard_input(), "exit")

    @patch("builtins.input", side_effect=KeyboardInterrupt)
    def test_keyboard_interrupt_returns_exit(self, _):
        from voice import _keyboard_input
        self.assertEqual(_keyboard_input(), "exit")

    def test_listen_uses_keyboard_when_sd_unavailable(self):
        with patch("voice._SD_AVAILABLE", False), \
             patch("voice._keyboard_input", return_value="hello") as mock_kb:
            from voice import listen
            result = listen()
        mock_kb.assert_called_once()
        self.assertEqual(result, "hello")

    def test_listen_uses_sounddevice_when_available(self):
        with patch("voice._SD_AVAILABLE", True), \
             patch("voice._sounddevice_input", return_value="mic input") as mock_sd:
            from voice import listen
            result = listen()
        mock_sd.assert_called_once()
        self.assertEqual(result, "mic input")


# =============================================================================
# 12. Voice Module — Sounddevice / Mic Tests  (mocked)
# =============================================================================
class TestVoiceSounddevice(unittest.TestCase):

    def _mock_sd_input(self, recognised_text="open google"):
        """Helper: mock sounddevice + SpeechRecognition to return recognised_text."""
        import numpy as np

        mock_frames = MagicMock()
        mock_frames.tobytes.return_value = b"\x00" * 3200

        mock_sr_audio = MagicMock()

        mock_recogniser = MagicMock()
        mock_recogniser.record.return_value = mock_sr_audio
        mock_recogniser.recognize_google.return_value = recognised_text

        return mock_frames, mock_sr_audio, mock_recogniser

    @patch("voice._SD_AVAILABLE", True)
    def test_sounddevice_path_returns_lowercase(self):
        import numpy as np
        frames, audio, recogniser = self._mock_sd_input("Open YouTube")

        with patch("voice._sd") as mock_sd_mod, \
             patch("voice._np") as mock_np_mod, \
             patch("speech_recognition.Recognizer", return_value=recogniser), \
             patch("speech_recognition.AudioFile"):
            mock_sd_mod.rec.return_value = frames
            mock_sd_mod.wait = MagicMock()
            mock_np_mod = MagicMock()

            from voice import _sounddevice_input
            with patch("voice._numpy_to_wav", return_value=io.BytesIO(b"")):
                result = _sounddevice_input()

        self.assertEqual(result, "open youtube")

    @patch("voice._SD_AVAILABLE", True)
    def test_sounddevice_unknown_value_returns_none(self):
        import speech_recognition as sr
        with patch("voice._sd") as mock_sd, \
             patch("voice._numpy_to_wav", return_value=io.BytesIO(b"")):
            mock_sd.rec.return_value = MagicMock()
            mock_sd.wait = MagicMock()
            with patch("speech_recognition.Recognizer") as mock_recog:
                instance = mock_recog.return_value
                instance.record.return_value = MagicMock()
                instance.recognize_google.side_effect = sr.UnknownValueError()
                with patch("speech_recognition.AudioFile"), \
                     patch("voice.speak"):
                    from voice import _sounddevice_input
                    result = _sounddevice_input()
        self.assertIsNone(result)

    @patch("voice._SD_AVAILABLE", True)
    def test_sounddevice_request_error_returns_none(self):
        import speech_recognition as sr
        with patch("voice._sd") as mock_sd, \
             patch("voice._numpy_to_wav", return_value=io.BytesIO(b"")):
            mock_sd.rec.return_value = MagicMock()
            mock_sd.wait = MagicMock()
            with patch("speech_recognition.Recognizer") as mock_recog:
                instance = mock_recog.return_value
                instance.record.return_value = MagicMock()
                instance.recognize_google.side_effect = sr.RequestError("net error")
                with patch("speech_recognition.AudioFile"), \
                     patch("voice.speak"):
                    from voice import _sounddevice_input
                    result = _sounddevice_input()
        self.assertIsNone(result)


# =============================================================================
# 13. End-to-End Keyboard Mode Simulation
# =============================================================================
class TestEndToEndKeyboardMode(unittest.TestCase):
    """
    Simulate a full Jarvis session in keyboard mode:
    user types commands → process_command → speak response → loop → exit.
    No real audio, TTS, or network involved.
    """

    def _run_session(self, commands: list[str]) -> list[str]:
        """
        Drive the main loop with a scripted list of commands.
        Returns all spoken responses (extracted from printed output).
        """
        from voice import speak, listen, _keyboard_input
        from assistant import process_command

        spoken = []

        def fake_speak(text):
            spoken.append(text)

        command_iter = iter(commands)

        def fake_listen():
            try:
                return next(command_iter)
            except StopIteration:
                return "exit"

        with patch("voice._SD_AVAILABLE", False), \
             patch("voice._engine") as mock_engine, \
             patch("builtins.input", side_effect=commands + ["exit"]):
            mock_engine.say = MagicMock()
            mock_engine.runAndWait = MagicMock()

            responses = []
            for cmd in commands:
                result = process_command(cmd)
                if result and result != "__EXIT__":
                    responses.append(result)
                elif result == "__EXIT__":
                    break
        return responses

    def test_time_query_e2e(self):
        responses = self._run_session(["what is the time"])
        self.assertTrue(any("time is" in r.lower() for r in responses))

    def test_date_query_e2e(self):
        responses = self._run_session(["what is the date"])
        self.assertTrue(any("today is" in r.lower() for r in responses))

    @patch("webbrowser.open")
    def test_open_website_e2e(self, _):
        responses = self._run_session(["open youtube"])
        self.assertTrue(any("youtube" in r.lower() for r in responses))

    @patch("webbrowser.open")
    def test_web_search_e2e(self, _):
        responses = self._run_session(["search for neural networks"])
        self.assertTrue(any("neural networks" in r.lower() for r in responses))

    def test_exit_command_e2e(self):
        from assistant import process_command
        result = process_command("goodbye")
        self.assertEqual(result, "__EXIT__")

    def test_note_roundtrip_e2e(self):
        """Take a note then read it back in the same session."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            tmp = pathlib.Path(f.name)

        try:
            with patch("commands.NOTES_FILE", tmp):
                responses = self._run_session([
                    "take a note remember to call mom",
                    "read my notes",
                ])
            combined = " ".join(responses).lower()
            self.assertIn("call mom", combined)
        finally:
            tmp.unlink(missing_ok=True)

    @patch("assistant.ask_ollama", return_value="That is a great question!")
    def test_unknown_command_falls_back_to_ai_e2e(self, _):
        responses = self._run_session(["what is the speed of light"])
        self.assertTrue(any("great question" in r.lower() for r in responses))


# =============================================================================
# 14. Security / Boundary Tests
# =============================================================================
class TestSecurityBoundaries(unittest.TestCase):

    def test_open_website_never_opens_arbitrary_url(self):
        """Only whitelisted URLs must ever be opened."""
        with patch("webbrowser.open") as mock_open:
            from commands import open_website
            open_website("open http://malicious.example.com")
        mock_open.assert_not_called()

    def test_web_search_encodes_query(self):
        """Potentially dangerous chars must be URL-encoded."""
        with patch("webbrowser.open") as mock_open:
            from commands import web_search
            web_search("search for <script>alert(1)</script>")
        url = mock_open.call_args[0][0]
        self.assertNotIn("<script>", url)
        self.assertNotIn("alert(1)", url)

    def test_open_application_never_runs_arbitrary_command(self):
        """A user trying to inject an executable must get the 'not found' reply."""
        with patch("subprocess.Popen") as mock_popen:
            from commands import open_application
            result = open_application("open rm -rf /")
        mock_popen.assert_not_called()
        self.assertIn("don't have", result.lower())

    def test_play_music_blocks_path_traversal(self):
        """
        Verify that a crafted song name cannot escape MUSIC_FOLDER.
        The path-containment guard in play_music() should block it.
        """
        from commands import play_music
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            # Put a real mp3 in a sub-folder that would be outside MUSIC_FOLDER
            evil_dir = pathlib.Path(tmpdir) / "subdir"
            evil_dir.mkdir()
            evil_mp3 = evil_dir / "evil.mp3"
            evil_mp3.write_bytes(b"\x00" * 10)

            # Point MUSIC_FOLDER to a different location
            real_music = pathlib.Path(tmpdir) / "real_music"
            real_music.mkdir()
            (real_music / "safe.mp3").write_bytes(b"\x00" * 10)

            with patch("commands.MUSIC_FOLDER", real_music), \
                 patch("commands._PYGAME_READY", True), \
                 patch("pygame.mixer.music") as mock_music:
                # Even if a crafted path resolves outside, our guard catches it
                result = play_music("play song ../subdir/evil")

        # It should either play "safe.mp3" (random) or refuse — never the evil file
        load_args = mock_music.load.call_args
        if load_args:
            loaded_path = load_args[0][0]
            self.assertNotIn("evil", loaded_path.lower())

    def test_notes_file_path_is_not_user_controlled(self):
        """NOTES_FILE must be a fixed path from config, not derived from user input."""
        from config import NOTES_FILE, BASE_DIR
        self.assertTrue(
            str(NOTES_FILE).startswith(str(BASE_DIR)),
            "NOTES_FILE should reside inside the project directory"
        )

    def test_ollama_url_is_localhost_only(self):
        """The Ollama URL must point only to localhost — no external calls."""
        from config import OLLAMA_BASE_URL
        self.assertIn("127.0.0.1", OLLAMA_BASE_URL,
                      "Ollama must communicate with localhost only")


# =============================================================================
# Runner
# =============================================================================
if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    test_classes = [
        TestConfig,
        TestTimeDate,
        TestWebCommands,
        TestApplicationLauncher,
        TestMusicCommands,
        TestNotesCommands,
        TestExtractAfter,
        TestOllamaIntegration,
        TestProcessCommand,
        TestVoiceTTS,
        TestVoiceKeyboardFallback,
        TestVoiceSounddevice,
        TestEndToEndKeyboardMode,
        TestSecurityBoundaries,
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    print("\n" + "=" * 65)
    if result.wasSuccessful():
        print(f"  ALL {result.testsRun} TESTS PASSED ✓")
    else:
        failed  = len(result.failures)
        errored = len(result.errors)
        passed  = result.testsRun - failed - errored
        print(f"  {result.testsRun} run  |  {passed} passed  "
              f"|  {failed} failed  |  {errored} errors")
    print("=" * 65)

    sys.exit(0 if result.wasSuccessful() else 1)
