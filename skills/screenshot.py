"""Screenshot Skill — capture the screen."""

import os
import tempfile
import datetime
from core.dispatcher import SkillBase, Intent


class Skill(SkillBase):
    name = "screenshot"
    description = "Take a screenshot"
    keywords = ["screenshot", "screen capture", "capture screen", "take a picture of the screen"]
    dangerous = False

    def match(self, text: str):
        t = text.lower().strip()
        for kw in self.keywords:
            if kw in t:
                return Intent(raw_text=text, skill_name=self.name,
                              action="capture", params={}, confidence=0.9)
        return None

    def execute(self, intent: Intent) -> str:
        try:
            import pyautogui
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            desktop = os.path.expanduser("~/Desktop")
            path = os.path.join(desktop, f"screenshot_{ts}.png")
            img = pyautogui.screenshot()
            img.save(path)
            return f"Screenshot saved to {path}"
        except Exception as e:
            return f"Couldn't take screenshot: {e}"
