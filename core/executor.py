"""Action Executor — runs skill actions with approval flow for dangerous operations."""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional

from core.sandbox import Sandbox, SandboxResult, RiskLevel, SandboxConfig

logger = logging.getLogger(__name__)


class ActionType(Enum):
    SHELL = "shell"
    APP_OPEN = "app_open"
    APP_CLOSE = "app_close"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    FILE_CREATE = "file_create"
    BROWSER = "browser"
    DICTATION = "dictation"
    SCREENSHOT = "screenshot"
    NOTIFICATION = "notification"
    SYSTEM_INFO = "system_info"


# Actions that always require approval
APPROVAL_REQUIRED = {
    ActionType.FILE_WRITE,
    ActionType.FILE_CREATE,
    ActionType.SHELL,
    ActionType.BROWSER,
    ActionType.APP_CLOSE,
}


@dataclass
class Action:
    """Represents an action to be executed."""
    action_type: ActionType
    params: dict[str, Any]
    description: str = ""
    requires_approval: bool = False

    def __post_init__(self):
        if self.action_type in APPROVAL_REQUIRED:
            self.requires_approval = True


@dataclass
class ActionResult:
    """Result of an action execution."""
    success: bool
    output: str = ""
    error: str = ""
    blocked: bool = False


class ActionBlockedError(Exception):
    """Raised when an action is blocked by the approval system."""
    pass


class Executor:
    """Executes actions with approval gating and sandbox enforcement."""

    def __init__(self, sandbox: Optional[Sandbox] = None, sandbox_mode: bool = True):
        self.sandbox = sandbox or Sandbox()
        self.sandbox_mode = sandbox_mode
        self._approval_callback: Optional[Callable[[Action], bool]] = None
        self._handlers: dict[ActionType, Callable] = {}
        self._register_default_handlers()

    def set_approval_callback(self, callback: Callable[[Action], bool]):
        """Set UI callback for approval prompts. Signature: (action) -> bool."""
        self._approval_callback = callback

    def register_handler(self, action_type: ActionType, handler: Callable):
        """Register a custom handler for an action type."""
        self._handlers[action_type] = handler

    def _register_default_handlers(self):
        """Register built-in action handlers."""
        self._handlers[ActionType.SHELL] = self._handle_shell
        self._handlers[ActionType.APP_OPEN] = self._handle_app_open
        self._handlers[ActionType.APP_CLOSE] = self._handle_app_close
        self._handlers[ActionType.FILE_READ] = self._handle_file_read
        self._handlers[ActionType.FILE_WRITE] = self._handle_file_write
        self._handlers[ActionType.SCREENSHOT] = self._handle_screenshot
        self._handlers[ActionType.NOTIFICATION] = self._handle_notification
        self._handlers[ActionType.SYSTEM_INFO] = self._handle_system_info

    def _request_approval(self, action: Action) -> bool:
        """Request user approval for an action."""
        if self._approval_callback:
            return self._approval_callback(action)
        logger.warning(f"No approval callback — blocking: {action.description}")
        return False

    def execute(self, action: Action) -> ActionResult:
        """Execute an action with approval checks."""
        needs_approval = action.requires_approval or self.sandbox_mode
        if needs_approval:
            approved = self._request_approval(action)
            if not approved:
                logger.info(f"Action blocked: {action.description}")
                return ActionResult(success=False, blocked=True,
                                    error="Action requires user approval")

        handler = self._handlers.get(action.action_type)
        if not handler:
            return ActionResult(success=False, error=f"No handler for {action.action_type.value}")

        try:
            return handler(action)
        except Exception as e:
            logger.exception(f"Action execution failed: {action.description}")
            return ActionResult(success=False, error=str(e))

    # --- Built-in Handlers ---

    def _handle_shell(self, action: Action) -> ActionResult:
        command = action.params.get("command", "")
        result: SandboxResult = self.sandbox.execute(command)
        if result.blocked:
            return ActionResult(success=False, blocked=True, error=result.stderr)
        return ActionResult(
            success=result.return_code == 0,
            output=result.stdout,
            error=result.stderr,
        )

    def _handle_app_open(self, action: Action) -> ActionResult:
        import subprocess, sys
        app = action.params.get("app_name", "")
        try:
            if sys.platform == "darwin":
                subprocess.Popen(["open", "-a", app])
            elif sys.platform == "win32":
                subprocess.Popen(["start", app], shell=True)
            else:
                subprocess.Popen([app])
            return ActionResult(success=True, output=f"Opened {app}")
        except Exception as e:
            return ActionResult(success=False, error=str(e))

    def _handle_app_close(self, action: Action) -> ActionResult:
        import psutil
        app = action.params.get("app_name", "").lower()
        killed = 0
        for proc in psutil.process_iter(["name"]):
            if app in (proc.info["name"] or "").lower():
                proc.terminate()
                killed += 1
        if killed:
            return ActionResult(success=True, output=f"Closed {killed} instance(s) of {app}")
        return ActionResult(success=False, error=f"No running process found for {app}")

    def _handle_file_read(self, action: Action) -> ActionResult:
        path = action.params.get("path", "")
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read(1_048_576)  # 1 MB cap
            return ActionResult(success=True, output=content)
        except Exception as e:
            return ActionResult(success=False, error=str(e))

    def _handle_file_write(self, action: Action) -> ActionResult:
        path = action.params.get("path", "")
        content = action.params.get("content", "")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return ActionResult(success=True, output=f"Written to {path}")
        except Exception as e:
            return ActionResult(success=False, error=str(e))

    def _handle_screenshot(self, action: Action) -> ActionResult:
        import pyautogui, tempfile, os
        path = action.params.get("path", os.path.join(tempfile.gettempdir(), "screenshot.png"))
        try:
            img = pyautogui.screenshot()
            img.save(path)
            return ActionResult(success=True, output=f"Screenshot saved to {path}")
        except Exception as e:
            return ActionResult(success=False, error=str(e))

    def _handle_notification(self, action: Action) -> ActionResult:
        import sys
        title = action.params.get("title", "VoiceSafeClaw")
        message = action.params.get("message", "")
        try:
            if sys.platform == "darwin":
                import subprocess
                subprocess.run([
                    "osascript", "-e",
                    f'display notification "{message}" with title "{title}"'
                ])
            return ActionResult(success=True, output=f"Notification sent: {message}")
        except Exception as e:
            return ActionResult(success=False, error=str(e))

    def _handle_system_info(self, action: Action) -> ActionResult:
        import psutil, platform
        info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "cpu_percent": psutil.cpu_percent(interval=0.5),
            "ram_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
        }
        output = "\n".join(f"{k}: {v}" for k, v in info.items())
        return ActionResult(success=True, output=output)
