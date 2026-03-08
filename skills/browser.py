"""Browser Skill — open URLs, tabs, and basic browser automation."""

import re
import subprocess
import sys
import webbrowser
from core.dispatcher import SkillBase, Intent


# Common site shortcuts
SITE_SHORTCUTS = {
    "gmail": "https://mail.google.com",
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
    "twitter": "https://twitter.com",
    "x": "https://x.com",
    "reddit": "https://www.reddit.com",
    "linkedin": "https://www.linkedin.com",
    "stack overflow": "https://stackoverflow.com",
}


class Skill(SkillBase):
    name = "browser"
    description = "Open URLs, websites, and browser tabs"
    keywords = ["go to", "open chrome", "open browser", "browse", "navigate to",
                "open safari", "open firefox", "search for", "google"]
    dangerous = True

    def match(self, text: str):
        t = text.lower().strip()
        for kw in self.keywords:
            if kw in t:
                return Intent(raw_text=text, skill_name=self.name,
                              action="browse", params={"text": text},
                              confidence=0.85)
        # URL pattern
        if re.search(r'https?://|www\.|\.\w{2,3}(?:/|$)', t):
            return Intent(raw_text=text, skill_name=self.name,
                          action="browse", params={"text": text}, confidence=0.9)
        return None

    def execute(self, intent: Intent) -> str:
        text = intent.params.get("text", "").lower()

        # Check for site shortcuts
        for name, url in SITE_SHORTCUTS.items():
            if name in text:
                webbrowser.open(url)
                return f"Opening {name}"

        # Extract URL
        url_match = re.search(r'(https?://\S+)', text)
        if url_match:
            webbrowser.open(url_match.group(1))
            return f"Opening {url_match.group(1)}"

        # "search for X" → Google search
        search_match = re.search(r'(?:search\s+(?:for\s+)?|google\s+)(.+)', text)
        if search_match:
            query = search_match.group(1).strip()
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return f"Searching Google for: {query}"

        # Fallback: open default browser
        webbrowser.open("https://www.google.com")
        return "Opening browser"
