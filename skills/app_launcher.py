"""App Launcher Skill — open/close applications by voice."""

import re
import subprocess
import sys
from core.dispatcher import SkillBase, Intent
from core.executor import Executor, Action, ActionType

_executor = Executor(sandbox_mode=False)


class Skill(SkillBase):
    name = "app_launcher"
    description = "Open or close any application"
    keywords = ["open", "launch", "start", "close", "quit", "exit"]
    dangerous = False

    def match(self, text: str):
        t = text.lower().strip()
        for kw in self.keywords:
            if kw in t:
                # Extract app name after keyword
                pattern = rf'{kw}\s+(.+?)(?:\s+and\s+|\s*$)'
                m = re.search(pattern, t)
                app = m.group(1).strip() if m else ""
                action = "close" if kw in ("close", "quit", "exit") else "open"
                return Intent(raw_text=text, skill_name=self.name,
                              action=action, params={"app_name": app}, confidence=0.85)
        return None

    def execute(self, intent: Intent) -> str:
        app = intent.params.get("app_name", "")
        if not app:
            return "Which app would you like me to open?"
        if intent.action == "close":
            r = _executor.execute(Action(
                action_type=ActionType.APP_CLOSE,
                params={"app_name": app},
                description=f"Close {app}",
            ))
        else:
            r = _executor.execute(Action(
                action_type=ActionType.APP_OPEN,
                params={"app_name": app},
                description=f"Open {app}",
            ))
        return r.output if r.success else f"Sorry, couldn't {intent.action} {app}: {r.error}"
