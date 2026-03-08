"""SafeClaw Engine — central orchestrator for VoiceSafeClaw."""

import logging
import os
import sys
import signal
import threading
from typing import Optional, Callable

from core.sandbox import Sandbox, SandboxConfig
from core.executor import Executor, Action, ActionResult
from core.dispatcher import Dispatcher, SkillBase

logger = logging.getLogger(__name__)


class VoiceSafeClawEngine:
    """Main engine: ties together sandbox, executor, dispatcher, and voice loop."""

    def __init__(self, sandbox_mode: bool = True):
        sandbox_config = SandboxConfig(
            timeout_seconds=30.0,
            allow_network=False,
        )
        self.sandbox = Sandbox(config=sandbox_config)
        self.executor = Executor(sandbox=self.sandbox, sandbox_mode=sandbox_mode)
        self.dispatcher = Dispatcher()
        self._running = False
        self._voice_loop = None
        self._approval_callback: Optional[Callable] = None

        # Wire sandbox approval through executor
        self.sandbox.set_approval_callback(
            lambda cmd, risk: self._on_approval_needed(
                Action(
                    action_type=__import__("core.executor", fromlist=["ActionType"]).ActionType.SHELL,
                    params={"command": cmd},
                    description=f"Shell: {cmd}",
                ),
            )
        )

    def set_approval_callback(self, callback: Callable[[Action], bool]):
        """Set the UI approval callback (Tauri sends this)."""
        self._approval_callback = callback
        self.executor.set_approval_callback(callback)

    def _on_approval_needed(self, action: Action) -> bool:
        if self._approval_callback:
            return self._approval_callback(action)
        return False

    def register_skill(self, skill: SkillBase):
        """Register a voice skill."""
        self.dispatcher.register(skill)

    def register_default_skills(self):
        """Auto-discover and register all built-in skills."""
        try:
            from skills import (
                app_launcher, file_manager, browser, shell,
                dictation, screenshot, calendar_skill, email_draft,
                notification, web_search,
            )
            skill_modules = [
                app_launcher, file_manager, browser, shell,
                dictation, screenshot, calendar_skill, email_draft,
                notification, web_search,
            ]
            for mod in skill_modules:
                if hasattr(mod, "Skill"):
                    self.register_skill(mod.Skill())
        except ImportError as e:
            logger.warning(f"Some skills failed to import: {e}")

    def process_command(self, text: str) -> str:
        """Process a spoken command through the full pipeline."""
        logger.info(f"Processing command: {text}")
        response = self.dispatcher.dispatch(text)
        logger.info(f"Response: {response}")
        return response

    def start(self):
        """Start the engine and voice loop."""
        if self._running:
            return
        self._running = True
        logger.info("VoiceSafeClaw engine started")
        self.register_default_skills()

        # Start voice loop in background thread
        try:
            from voice.loop import VoiceLoop
            self._voice_loop = VoiceLoop(engine=self)
            loop_thread = threading.Thread(target=self._voice_loop.run, daemon=True)
            loop_thread.start()
            logger.info("Voice loop started")
        except ImportError:
            logger.warning("Voice module not available — running in text-only mode")

    def stop(self):
        """Stop the engine."""
        self._running = False
        if self._voice_loop:
            self._voice_loop.stop()
        logger.info("VoiceSafeClaw engine stopped")

    @property
    def is_running(self) -> bool:
        return self._running


def _setup_logging():
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    """CLI entry point."""
    _setup_logging()
    logger.info("=== VoiceSafeClaw v1.0 ===")

    sandbox_mode = os.environ.get("SANDBOX_MODE", "true").lower() == "true"
    engine = VoiceSafeClawEngine(sandbox_mode=sandbox_mode)

    # Default approval: console prompt
    def console_approval(action: Action) -> bool:
        print(f"\n⚠️  Action requires approval: {action.description}")
        print(f"   Type: {action.action_type.value}")
        resp = input("   Approve? [y/N]: ").strip().lower()
        return resp in ("y", "yes")

    engine.set_approval_callback(console_approval)

    def signal_handler(sig, frame):
        engine.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    engine.start()

    # Keep main thread alive
    print("\n🎙️  VoiceSafeClaw is listening... (Ctrl+C to quit)")
    print("   Say 'Hey Jarvis' followed by a command.\n")

    try:
        while engine.is_running:
            import time
            time.sleep(0.5)
    except KeyboardInterrupt:
        engine.stop()


if __name__ == "__main__":
    main()
