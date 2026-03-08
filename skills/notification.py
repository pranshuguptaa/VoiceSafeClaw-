"""Notification Skill — send system notifications."""

import subprocess
import sys
from core.dispatcher import SkillBase, Intent


class Skill(SkillBase):
    name = "notification"
    description = "Send system notifications and reminders"
    keywords = ["notify", "notification", "remind me", "alert", "send notification"]
    dangerous = False

    def match(self, text: str):
        t = text.lower().strip()
        for kw in self.keywords:
            if kw in t:
                idx = t.index(kw) + len(kw)
                message = text[idx:].strip()
                return Intent(raw_text=text, skill_name=self.name,
                              action="notify", params={"message": message},
                              confidence=0.8)
        return None

    def execute(self, intent: Intent) -> str:
        message = intent.params.get("message", "").strip()
        if not message:
            return "What should the notification say?"
        try:
            if sys.platform == "darwin":
                subprocess.run([
                    "osascript", "-e",
                    f'display notification "{message}" with title "VoiceSafeClaw"'
                ], check=True)
            elif sys.platform == "win32":
                ps = (
                    "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null;"
                    f'$t = [Windows.UI.Notifications.ToastNotification]::New((New-Object Windows.Data.Xml.Dom.XmlDocument)); '
                    f'$t.Content.LoadXml("<toast><visual><binding template=\'ToastText01\'><text id=\'1\'>{message}</text></binding></visual></toast>"); '
                    f'[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("VoiceSafeClaw").Show($t)'
                )
                subprocess.run(["powershell", "-Command", ps])
            return f"Notification sent: {message}"
        except Exception as e:
            return f"Couldn't send notification: {e}"
