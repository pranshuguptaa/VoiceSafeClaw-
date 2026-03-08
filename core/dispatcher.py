"""Skill Dispatcher — intent matching, skill registry, and routing."""

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class Intent:
    """Parsed user intent from speech."""
    raw_text: str
    skill_name: str = ""
    action: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0


class SkillBase:
    """Base class for all voice skills."""
    name: str = "base"
    description: str = ""
    keywords: list[str] = []
    dangerous: bool = False

    def match(self, text: str) -> Optional[Intent]:
        """Check if this skill matches the user's spoken text.
        Returns Intent with confidence 0.0-1.0, or None if no match."""
        text_lower = text.lower().strip()
        for keyword in self.keywords:
            if keyword in text_lower:
                return Intent(
                    raw_text=text,
                    skill_name=self.name,
                    confidence=0.8,
                    params={"text": text},
                )
        return None

    def execute(self, intent: Intent) -> str:
        """Execute the skill and return a spoken response string."""
        raise NotImplementedError


class Dispatcher:
    """Routes spoken text to the best-matching skill."""

    def __init__(self):
        self._skills: dict[str, SkillBase] = {}

    @property
    def skills(self) -> dict[str, SkillBase]:
        return dict(self._skills)

    def register(self, skill: SkillBase):
        """Register a skill."""
        self._skills[skill.name] = skill
        logger.info(f"Registered skill: {skill.name}")

    def unregister(self, name: str):
        """Remove a skill by name."""
        self._skills.pop(name, None)

    def enable_skill(self, name: str, enabled: bool = True):
        """Enable/disable a skill (for settings UI)."""
        if name in self._skills:
            self._skills[name]._enabled = enabled

    def match(self, text: str) -> Optional[Intent]:
        """Find the best-matching skill for spoken text."""
        best_intent: Optional[Intent] = None
        best_confidence = 0.0

        for skill in self._skills.values():
            if getattr(skill, "_enabled", True) is False:
                continue
            intent = skill.match(text)
            if intent and intent.confidence > best_confidence:
                best_intent = intent
                best_confidence = intent.confidence

        if best_intent:
            logger.info(f"Matched skill '{best_intent.skill_name}' "
                        f"(confidence={best_confidence:.2f}) for: {text}")
        else:
            logger.info(f"No skill matched for: {text}")

        return best_intent

    def dispatch(self, text: str) -> str:
        """Match text to a skill and execute it. Returns spoken response."""
        intent = self.match(text)
        if not intent:
            return "Sorry, I didn't understand that command."

        skill = self._skills.get(intent.skill_name)
        if not skill:
            return "Sorry, that skill is not available."

        try:
            return skill.execute(intent)
        except Exception as e:
            logger.exception(f"Skill '{intent.skill_name}' failed")
            return f"Sorry, there was an error: {e}"

    def list_skills(self) -> list[dict[str, Any]]:
        """Return skill metadata for the settings UI."""
        return [
            {
                "name": s.name,
                "description": s.description,
                "dangerous": s.dangerous,
                "enabled": getattr(s, "_enabled", True),
            }
            for s in self._skills.values()
        ]
