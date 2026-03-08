"""Shell Skill — execute shell commands with sandbox approval."""

import re
from core.dispatcher import SkillBase, Intent
from core.executor import Executor, Action, ActionType

_executor = Executor(sandbox_mode=True)


class Skill(SkillBase):
    name = "shell"
    description = "Run shell/terminal commands"
    keywords = ["run command", "execute", "terminal", "shell", "run script",
                "command line", "run python", "run pip"]
    dangerous = True

    def match(self, text: str):
        t = text.lower().strip()
        for kw in self.keywords:
            if kw in t:
                # Extract the command after the keyword
                idx = t.index(kw) + len(kw)
                cmd = text[idx:].strip().strip('"').strip("'")
                return Intent(raw_text=text, skill_name=self.name,
                              action="run", params={"command": cmd},
                              confidence=0.85)
        return None

    def execute(self, intent: Intent) -> str:
        cmd = intent.params.get("command", "").strip()
        if not cmd:
            return "What command should I run?"

        r = _executor.execute(Action(
            action_type=ActionType.SHELL,
            params={"command": cmd},
            description=f"Shell: {cmd}",
        ))
        if r.blocked:
            return f"Command blocked — requires approval: {cmd}"
        if r.success:
            output = r.output.strip()
            return f"Command completed. Output: {output[:300]}" if output else "Command completed successfully."
        return f"Command failed: {r.error[:200]}"
