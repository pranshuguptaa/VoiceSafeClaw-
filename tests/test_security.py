"""Security tests — verify dangerous actions are blocked without approval."""

import pytest
from core.sandbox import Sandbox, SandboxConfig, RiskLevel
from core.executor import Executor, Action, ActionType, ActionResult


class TestSecurityBlocking:
    """All dangerous actions MUST be blocked without explicit approval."""

    def test_rm_rf_blocked(self):
        s = Sandbox()
        result = s.execute("rm -rf /")
        assert result.blocked
        assert result.risk_level == RiskLevel.DANGEROUS

    def test_sudo_blocked(self):
        s = Sandbox()
        result = s.execute("sudo shutdown now")
        assert result.blocked

    def test_format_blocked(self):
        s = Sandbox()
        result = s.execute("format C:")
        assert result.blocked

    def test_dd_blocked(self):
        s = Sandbox()
        result = s.execute("dd if=/dev/zero of=/dev/sda")
        assert result.blocked

    def test_fork_bomb_blocked(self):
        s = Sandbox()
        result = s.execute(":(){ :|:& };:")
        assert result.blocked

    def test_safe_command_not_blocked(self):
        s = Sandbox()
        result = s.execute("echo safe")
        assert not result.blocked
        assert result.risk_level == RiskLevel.SAFE

    def test_executor_blocks_without_callback(self):
        """Executor with no approval callback blocks dangerous actions."""
        e = Executor(sandbox_mode=True)
        # No approval callback set → should block
        action = Action(
            action_type=ActionType.FILE_WRITE,
            params={"path": "/tmp/test", "content": "x"},
            description="Write test file",
        )
        result = e.execute(action)
        assert result.blocked
        assert not result.success

    def test_executor_allows_with_approval(self):
        """Executor with approval callback that returns True allows action."""
        e = Executor(sandbox_mode=True)
        e.set_approval_callback(lambda action: True)
        action = Action(
            action_type=ActionType.SHELL,
            params={"command": "echo approved"},
            description="Echo test",
        )
        result = e.execute(action)
        assert not result.blocked
        assert result.success

    def test_executor_rejects_with_denial(self):
        """Executor with approval callback that returns False blocks."""
        e = Executor(sandbox_mode=True)
        e.set_approval_callback(lambda action: False)
        action = Action(
            action_type=ActionType.SHELL,
            params={"command": "echo denied"},
            description="Echo test",
        )
        result = e.execute(action)
        assert result.blocked

    def test_sandbox_mode_blocks_all(self):
        """In sandbox mode, even safe actions need approval."""
        e = Executor(sandbox_mode=True)
        # No callback → blocks all
        action = Action(
            action_type=ActionType.SYSTEM_INFO,
            params={},
            description="Get system info",
        )
        result = e.execute(action)
        assert result.blocked

    def test_non_sandbox_allows_safe(self):
        """Without sandbox mode, safe actions go through."""
        e = Executor(sandbox_mode=False)
        action = Action(
            action_type=ActionType.SYSTEM_INFO,
            params={},
            description="Get system info",
        )
        result = e.execute(action)
        assert not result.blocked
        assert result.success


class TestRiskAssessment:
    """Verify risk classification is comprehensive."""

    @pytest.mark.parametrize("cmd,expected", [
        ("echo hello", RiskLevel.SAFE),
        ("ls -la", RiskLevel.SAFE),
        ("pwd", RiskLevel.SAFE),
        ("rm file.txt", RiskLevel.MODERATE),
        ("mv a b", RiskLevel.MODERATE),
        ("pip install flask", RiskLevel.MODERATE),
        ("rm -rf /", RiskLevel.DANGEROUS),
        ("sudo rm file", RiskLevel.DANGEROUS),
        ("chmod 777 /etc/passwd", RiskLevel.DANGEROUS),
        ("shutdown -h now", RiskLevel.DANGEROUS),
    ])
    def test_risk_levels(self, cmd, expected):
        s = Sandbox()
        assert s.assess_risk(cmd) == expected
