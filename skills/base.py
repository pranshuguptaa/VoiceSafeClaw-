"""Base Skill — abstract base class for all VoiceSafeClaw skills."""

from core.dispatcher import SkillBase, Intent
from core.executor import Executor, Action, ActionType, ActionResult

__all__ = ["SkillBase", "Intent", "Executor", "Action", "ActionType", "ActionResult"]
