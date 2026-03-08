"""File Manager Skill — read, write, create files and folders."""

import os
import re
from core.dispatcher import SkillBase, Intent
from core.executor import Executor, Action, ActionType

_executor = Executor(sandbox_mode=True)


class Skill(SkillBase):
    name = "file_manager"
    description = "Read, write, and create files or folders"
    keywords = ["read file", "write file", "create file", "create folder",
                "make folder", "show file", "edit file", "new file"]
    dangerous = True

    def match(self, text: str):
        t = text.lower().strip()
        for kw in self.keywords:
            if kw in t:
                action = "read" if "read" in kw or "show" in kw else "write"
                if "folder" in kw:
                    action = "mkdir"
                # Try to find a file path or name
                path_match = re.search(r'(?:called|named|at|path)?\s*[\"\']?([/~][\w./\-]+|[\w.\-]+\.\w+)', t)
                path = path_match.group(1) if path_match else ""
                return Intent(raw_text=text, skill_name=self.name,
                              action=action, params={"path": path, "text": text},
                              confidence=0.8)
        return None

    def execute(self, intent: Intent) -> str:
        path = intent.params.get("path", "")
        if not path:
            return "Please specify a file name or path."
        path = os.path.expanduser(path)

        if intent.action == "read":
            r = _executor.execute(Action(
                action_type=ActionType.FILE_READ,
                params={"path": path},
                description=f"Read file: {path}",
            ))
            if r.success:
                preview = r.output[:500]
                return f"Here's the content of {os.path.basename(path)}: {preview}"
            return f"Couldn't read {path}: {r.error}"

        elif intent.action == "mkdir":
            try:
                os.makedirs(path, exist_ok=True)
                return f"Created folder: {path}"
            except Exception as e:
                return f"Couldn't create folder: {e}"

        else:  # write
            content = intent.params.get("content", "")
            r = _executor.execute(Action(
                action_type=ActionType.FILE_WRITE,
                params={"path": path, "content": content},
                description=f"Write file: {path}",
            ))
            return r.output if r.success else f"Couldn't write to {path}: {r.error}"
