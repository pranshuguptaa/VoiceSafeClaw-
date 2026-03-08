"""Integration tests for all 10 voice skills."""

import pytest
from unittest.mock import patch, MagicMock
from core.dispatcher import Intent


class TestAppLauncher:
    def test_match_open(self):
        from skills.app_launcher import Skill
        s = Skill()
        intent = s.match("open calculator")
        assert intent is not None
        assert intent.params["app_name"] == "calculator"
        assert intent.action == "open"

    def test_match_close(self):
        from skills.app_launcher import Skill
        s = Skill()
        intent = s.match("close safari")
        assert intent is not None
        assert intent.action == "close"

    def test_no_match(self):
        from skills.app_launcher import Skill
        s = Skill()
        assert s.match("what time is it") is None


class TestFileManager:
    def test_match_read(self):
        from skills.file_manager import Skill
        s = Skill()
        intent = s.match("read file /tmp/test.txt")
        assert intent is not None
        assert intent.action == "read"

    def test_match_create_folder(self):
        from skills.file_manager import Skill
        s = Skill()
        intent = s.match("create folder /tmp/testdir")
        assert intent is not None
        assert intent.action == "mkdir"

    def test_no_match(self):
        from skills.file_manager import Skill
        s = Skill()
        assert s.match("open chrome") is None


class TestBrowser:
    def test_match_go_to(self):
        from skills.browser import Skill
        s = Skill()
        intent = s.match("go to gmail")
        assert intent is not None

    def test_match_url(self):
        from skills.browser import Skill
        s = Skill()
        intent = s.match("open https://example.com")
        assert intent is not None

    @patch("webbrowser.open")
    def test_execute_shortcut(self, mock_open):
        from skills.browser import Skill
        s = Skill()
        intent = Intent(raw_text="go to gmail", skill_name="browser",
                        action="browse", params={"text": "go to gmail"})
        result = s.execute(intent)
        mock_open.assert_called_once_with("https://mail.google.com")
        assert "gmail" in result.lower()


class TestShell:
    def test_match(self):
        from skills.shell import Skill
        s = Skill()
        intent = s.match("run command echo hi")
        assert intent is not None
        assert "echo hi" in intent.params["command"]

    def test_no_match(self):
        from skills.shell import Skill
        s = Skill()
        assert s.match("open calculator") is None


class TestDictation:
    def test_match(self):
        from skills.dictation import Skill
        s = Skill()
        intent = s.match("type hello world")
        assert intent is not None
        assert "hello world" in intent.params["content"]


class TestScreenshot:
    def test_match(self):
        from skills.screenshot import Skill
        s = Skill()
        intent = s.match("take a screenshot")
        assert intent is not None
        assert intent.action == "capture"

    @patch("pyautogui.screenshot")
    def test_execute(self, mock_ss):
        from skills.screenshot import Skill
        mock_img = MagicMock()
        mock_ss.return_value = mock_img
        s = Skill()
        intent = Intent(raw_text="screenshot", skill_name="screenshot",
                        action="capture", params={})
        result = s.execute(intent)
        assert "saved" in result.lower()
        mock_img.save.assert_called_once()


class TestCalendar:
    def test_match_time(self):
        from skills.calendar_skill import Skill
        s = Skill()
        intent = s.match("what time is it")
        assert intent is not None

    def test_execute_time(self):
        from skills.calendar_skill import Skill
        s = Skill()
        intent = Intent(raw_text="what time", skill_name="calendar",
                        action="info", params={"text": "what time"})
        result = s.execute(intent)
        assert "currently" in result.lower() or ":" in result


class TestEmailDraft:
    def test_match(self):
        from skills.email_draft import Skill
        s = Skill()
        intent = s.match("send email to bob@example.com")
        assert intent is not None

    @patch("webbrowser.open")
    def test_execute(self, mock_open):
        from skills.email_draft import Skill
        s = Skill()
        intent = Intent(raw_text="email to test@test.com about meeting",
                        skill_name="email_draft", action="draft",
                        params={"text": "email to test@test.com about meeting"})
        result = s.execute(intent)
        mock_open.assert_called_once()
        assert "draft" in result.lower() or "email" in result.lower()


class TestNotification:
    @patch("subprocess.run")
    def test_execute(self, mock_run):
        from skills.notification import Skill
        s = Skill()
        intent = Intent(raw_text="notify hello", skill_name="notification",
                        action="notify", params={"message": "hello"})
        result = s.execute(intent)
        assert "sent" in result.lower() or "notification" in result.lower()


class TestWebSearch:
    def test_match_local_qa(self):
        from skills.web_search import Skill
        s = Skill()
        intent = s.match("who are you")
        assert intent is not None
        assert intent.action == "local"

    def test_execute_local(self):
        from skills.web_search import Skill
        s = Skill()
        intent = Intent(raw_text="who are you", skill_name="web_search",
                        action="local", params={"answer": "I'm Jarvis"})
        result = s.execute(intent)
        assert "Jarvis" in result

    @patch("webbrowser.open")
    def test_execute_search(self, mock_open):
        from skills.web_search import Skill
        s = Skill()
        intent = Intent(raw_text="what is python", skill_name="web_search",
                        action="search", params={"query": "what is python"})
        result = s.execute(intent)
        mock_open.assert_called_once()
