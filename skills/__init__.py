"""VoiceSafeClaw Skills — 10 pre-built voice command skills."""

from skills import (
    app_launcher,
    file_manager,
    browser,
    shell,
    dictation,
    screenshot,
    calendar_skill,
    email_draft,
    notification,
    web_search,
)

ALL_SKILLS = [
    app_launcher, file_manager, browser, shell, dictation,
    screenshot, calendar_skill, email_draft, notification, web_search,
]

__all__ = ["ALL_SKILLS"]
