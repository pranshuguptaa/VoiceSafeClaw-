"""SafeClaw Sandbox — isolated process execution with resource limits."""

import subprocess
import threading
import logging
import os
import signal
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    SAFE = "safe"
    MODERATE = "moderate"
    DANGEROUS = "dangerous"


# Commands/patterns that require explicit approval
DANGEROUS_PATTERNS = [
    "rm -rf", "rmdir", "del /s", "format", "mkfs",
    "sudo", "chmod 777", "shutdown", "reboot",
    "> /dev/", "dd if=", ":(){ :|:& };:",
]

MODERATE_PATTERNS = [
    "rm ", "mv ", "cp ", "mkdir", "touch",
    "kill", "pkill", "pip install", "brew install",
    "npm install", "apt install",
]


@dataclass
class SandboxResult:
    """Result of a sandboxed command execution."""
    stdout: str = ""
    stderr: str = ""
    return_code: int = -1
    timed_out: bool = False
    blocked: bool = False
    risk_level: RiskLevel = RiskLevel.SAFE


@dataclass
class SandboxConfig:
    """Configuration for sandbox execution."""
    timeout_seconds: float = 30.0
    max_output_bytes: int = 1_048_576  # 1 MB
    allow_network: bool = False
    working_dir: Optional[str] = None
    env_whitelist: list[str] = field(default_factory=lambda: [
        "PATH", "HOME", "USER", "SHELL", "LANG", "TERM",
    ])


class Sandbox:
    """Executes commands in a restricted sandbox environment."""

    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or SandboxConfig()
        self._approval_callback = None

    def set_approval_callback(self, callback):
        """Set callback for requesting user approval. Signature: (cmd, risk) -> bool."""
        self._approval_callback = callback

    def assess_risk(self, command: str) -> RiskLevel:
        """Assess the risk level of a command."""
        cmd_lower = command.lower().strip()
        for pattern in DANGEROUS_PATTERNS:
            if pattern in cmd_lower:
                return RiskLevel.DANGEROUS
        for pattern in MODERATE_PATTERNS:
            if pattern in cmd_lower:
                return RiskLevel.MODERATE
        return RiskLevel.SAFE

    def _get_safe_env(self) -> dict[str, str]:
        """Build a sanitized environment dict."""
        env = {}
        for key in self.config.env_whitelist:
            if key in os.environ:
                env[key] = os.environ[key]
        return env

    def _request_approval(self, command: str, risk: RiskLevel) -> bool:
        """Request user approval for risky commands."""
        if self._approval_callback:
            return self._approval_callback(command, risk)
        # Default: block dangerous, allow moderate with warning
        if risk == RiskLevel.DANGEROUS:
            logger.warning(f"BLOCKED dangerous command (no approval callback): {command}")
            return False
        if risk == RiskLevel.MODERATE:
            logger.info(f"Auto-approved moderate command (no callback): {command}")
            return True
        return True

    def execute(self, command: str) -> SandboxResult:
        """Execute a command inside the sandbox."""
        risk = self.assess_risk(command)
        result = SandboxResult(risk_level=risk)

        if risk != RiskLevel.SAFE:
            approved = self._request_approval(command, risk)
            if not approved:
                result.blocked = True
                result.stderr = f"Action blocked: {risk.value} risk command requires approval"
                logger.info(f"Blocked {risk.value} command: {command}")
                return result

        try:
            env = self._get_safe_env()
            cwd = self.config.working_dir or os.path.expanduser("~")

            proc = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=cwd,
                preexec_fn=os.setsid if os.name != "nt" else None,
            )

            try:
                stdout, stderr = proc.communicate(timeout=self.config.timeout_seconds)
                result.stdout = stdout.decode("utf-8", errors="replace")[: self.config.max_output_bytes]
                result.stderr = stderr.decode("utf-8", errors="replace")[: self.config.max_output_bytes]
                result.return_code = proc.returncode
            except subprocess.TimeoutExpired:
                if os.name != "nt":
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                else:
                    proc.kill()
                proc.wait()
                result.timed_out = True
                result.stderr = f"Command timed out after {self.config.timeout_seconds}s"

        except Exception as e:
            result.stderr = f"Sandbox execution error: {e}"
            result.return_code = -1
            logger.exception(f"Sandbox error running: {command}")

        return result
