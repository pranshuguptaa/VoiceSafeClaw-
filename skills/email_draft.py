"""Email Draft Skill — compose email drafts via mailto link."""

import re
import webbrowser
import urllib.parse
from core.dispatcher import SkillBase, Intent


class Skill(SkillBase):
    name = "email_draft"
    description = "Compose and open email drafts"
    keywords = ["email", "send email", "compose email", "draft email",
                "write email", "mail to", "send a message to"]
    dangerous = False

    def match(self, text: str):
        t = text.lower().strip()
        for kw in self.keywords:
            if kw in t:
                return Intent(raw_text=text, skill_name=self.name,
                              action="draft", params={"text": text},
                              confidence=0.8)
        return None

    def execute(self, intent: Intent) -> str:
        text = intent.params.get("text", "")
        # Try to extract recipient
        to_match = re.search(r'(?:to|for)\s+([\w.+-]+@[\w-]+\.[\w.]+)', text, re.I)
        to = to_match.group(1) if to_match else ""
        # Try to extract subject
        subj_match = re.search(r'(?:about|subject|regarding)\s+(.+?)(?:\s+saying|\s*$)', text, re.I)
        subject = subj_match.group(1).strip() if subj_match else ""
        # Try to extract body
        body_match = re.search(r'(?:saying|body|message)\s+(.+)', text, re.I)
        body = body_match.group(1).strip() if body_match else ""

        params = urllib.parse.urlencode({"subject": subject, "body": body})
        mailto = f"mailto:{to}?{params}"
        webbrowser.open(mailto)
        return f"Email draft opened{' to ' + to if to else ''}"
