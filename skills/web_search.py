"""Web Search / Q&A Skill — answer general questions or search the web."""

import re
import webbrowser
import subprocess
import sys
import json
from core.dispatcher import SkillBase, Intent


# Simple local Q&A for common questions (no internet needed)
LOCAL_ANSWERS = {
    "who are you": "I'm Jarvis, your local voice assistant powered by VoiceSafeClaw.",
    "what can you do": "I can open apps, manage files, browse the web, run commands, take screenshots, dictate text, and more.",
    "how are you": "I'm running smoothly, thank you for asking!",
}


class Skill(SkillBase):
    name = "web_search"
    description = "Answer questions or search the web"
    keywords = ["what is", "what's", "who is", "where is", "how to",
                "tell me", "what are", "why", "when", "weather",
                "define", "meaning of", "how much", "how many"]
    dangerous = False

    def match(self, text: str):
        t = text.lower().strip()
        # Local Q&A first
        for q in LOCAL_ANSWERS:
            if q in t:
                return Intent(raw_text=text, skill_name=self.name,
                              action="local", params={"answer": LOCAL_ANSWERS[q]},
                              confidence=0.95)
        for kw in self.keywords:
            if t.startswith(kw) or kw in t:
                return Intent(raw_text=text, skill_name=self.name,
                              action="search", params={"query": text},
                              confidence=0.6)  # Lower confidence = fallback
        return None

    def execute(self, intent: Intent) -> str:
        if intent.action == "local":
            return intent.params.get("answer", "")

        query = intent.params.get("query", "")
        if not query:
            return "What would you like to know?"

        # Open Google search (works offline-safe — just opens browser)
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Searching for: {query}"
