"""Dictation Skill — type text anywhere using accessibility/clipboard."""

import sys
import time
from core.dispatcher import SkillBase, Intent


class Skill(SkillBase):
    name = "dictation"
    description = "Dictate and auto-type text anywhere"
    keywords = ["type", "dictate", "write this", "type this"]
    dangerous = False

    def match(self, text: str):
        t = text.lower().strip()
        for kw in self.keywords:
            if t.startswith(kw) or kw in t:
                idx = t.index(kw) + len(kw)
                content = text[idx:].strip().strip('"').strip("'")
                return Intent(raw_text=text, skill_name=self.name,
                              action="type", params={"content": content},
                              confidence=0.85)
        return None

    def execute(self, intent: Intent) -> str:
        content = intent.params.get("content", "")
        if not content:
            return "What would you like me to type?"
        try:
            import pyperclip
            import pyautogui
            pyperclip.copy(content)
            time.sleep(0.1)
            # Paste using Cmd+V (mac) or Ctrl+V (win)
            mod = "command" if sys.platform == "darwin" else "ctrl"
            pyautogui.hotkey(mod, "v")
            return f"Typed: {content[:50]}..."
        except Exception as e:
            return f"Couldn't type text: {e}"
