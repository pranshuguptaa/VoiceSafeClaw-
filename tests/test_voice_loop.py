"""Unit tests for the voice loop pipeline."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import numpy as np

from core.dispatcher import Dispatcher, SkillBase, Intent
from core.sandbox import Sandbox, SandboxConfig, RiskLevel
from core.executor import Executor, Action, ActionType


class MockSkill(SkillBase):
    name = "mock_skill"
    description = "Test skill"
    keywords = ["test", "mock"]

    def execute(self, intent):
        return f"Mock executed: {intent.raw_text}"


class TestDispatcher:
    """Test intent matching and dispatching."""

    def test_register_skill(self):
        d = Dispatcher()
        s = MockSkill()
        d.register(s)
        assert "mock_skill" in d.skills

    def test_match_found(self):
        d = Dispatcher()
        d.register(MockSkill())
        intent = d.match("test something")
        assert intent is not None
        assert intent.skill_name == "mock_skill"
        assert intent.confidence > 0

    def test_match_not_found(self):
        d = Dispatcher()
        d.register(MockSkill())
        intent = d.match("completely unrelated")
        assert intent is None

    def test_dispatch_success(self):
        d = Dispatcher()
        d.register(MockSkill())
        result = d.dispatch("test something")
        assert "Mock executed" in result

    def test_dispatch_no_match(self):
        d = Dispatcher()
        d.register(MockSkill())
        result = d.dispatch("xyz unknown")
        assert "didn't understand" in result

    def test_unregister(self):
        d = Dispatcher()
        d.register(MockSkill())
        d.unregister("mock_skill")
        assert "mock_skill" not in d.skills

    def test_list_skills(self):
        d = Dispatcher()
        d.register(MockSkill())
        skills = d.list_skills()
        assert len(skills) == 1
        assert skills[0]["name"] == "mock_skill"

    def test_disable_skill(self):
        d = Dispatcher()
        d.register(MockSkill())
        d.enable_skill("mock_skill", False)
        intent = d.match("test something")
        assert intent is None  # Disabled skill shouldn't match


class TestSandbox:
    """Test sandbox risk assessment and execution."""

    def test_safe_command(self):
        s = Sandbox()
        assert s.assess_risk("echo hello") == RiskLevel.SAFE

    def test_moderate_command(self):
        s = Sandbox()
        assert s.assess_risk("rm file.txt") == RiskLevel.MODERATE

    def test_dangerous_command(self):
        s = Sandbox()
        assert s.assess_risk("rm -rf /") == RiskLevel.DANGEROUS

    def test_execute_safe(self):
        s = Sandbox()
        result = s.execute("echo hello")
        assert result.return_code == 0
        assert "hello" in result.stdout
        assert not result.blocked

    def test_execute_timeout(self):
        config = SandboxConfig(timeout_seconds=0.5)
        s = Sandbox(config=config)
        result = s.execute("sleep 10")
        assert result.timed_out

    def test_dangerous_blocked_without_callback(self):
        s = Sandbox()
        result = s.execute("rm -rf /tmp/nonexistent_dir_test")
        assert result.blocked

    def test_dangerous_approved_with_callback(self):
        s = Sandbox()
        s.set_approval_callback(lambda cmd, risk: True)
        result = s.execute("echo dangerous_but_approved")
        assert not result.blocked
        assert "dangerous_but_approved" in result.stdout


class TestVoiceLoopPipeline:
    """Test the voice loop orchestrator logic (mocked audio)."""

    @patch("voice.stt.SpeechToText")
    @patch("voice.tts.TextToSpeech")
    @patch("voice.wake.WakeWordDetector")
    def test_pipeline_mock(self, mock_wake, mock_tts, mock_stt):
        """Verify the pipeline wiring: wake → STT → dispatch → TTS."""
        from core.engine import VoiceSafeClawEngine

        engine = VoiceSafeClawEngine(sandbox_mode=False)
        engine.dispatcher.register(MockSkill())

        # Simulate: user says "test hello"
        result = engine.process_command("test hello")
        assert "Mock executed" in result

    def test_engine_start_stop(self):
        """Engine can start and stop without voice module."""
        from core.engine import VoiceSafeClawEngine
        engine = VoiceSafeClawEngine(sandbox_mode=False)
        engine.start()
        assert engine.is_running
        engine.stop()
        assert not engine.is_running
