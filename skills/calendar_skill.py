"""Calendar Skill — quick calendar info and date lookups."""

import datetime
from core.dispatcher import SkillBase, Intent


class Skill(SkillBase):
    name = "calendar"
    description = "Date, time, and calendar information"
    keywords = ["what day", "what time", "what date", "today", "calendar",
                "what's the date", "what's the time", "current time"]
    dangerous = False

    def match(self, text: str):
        t = text.lower().strip()
        for kw in self.keywords:
            if kw in t:
                return Intent(raw_text=text, skill_name=self.name,
                              action="info", params={"text": text},
                              confidence=0.8)
        return None

    def execute(self, intent: Intent) -> str:
        now = datetime.datetime.now()
        text = intent.params.get("text", "").lower()

        if "time" in text:
            return f"It's currently {now.strftime('%I:%M %p')}"
        elif "day" in text:
            return f"Today is {now.strftime('%A, %B %d, %Y')}"
        else:
            return (f"Today is {now.strftime('%A, %B %d, %Y')} "
                    f"and the time is {now.strftime('%I:%M %p')}")
