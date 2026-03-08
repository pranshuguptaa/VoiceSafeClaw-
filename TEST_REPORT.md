# VoiceSafeClaw v1.0 — Test Report

**Date:** 2026-03-08
**Platform:** macOS (darwin), Python 3.14.3
**Duration:** 1.28s
**Result:** ✅ **60/60 PASSED — 0 warnings**

---

## Summary

| Suite                          | File                 | Tests  | Status        |
| ------------------------------ | -------------------- | ------ | ------------- |
| Security                       | `test_security.py`   | 21     | ✅ All passed |
| Skills Integration             | `test_skills.py`     | 19     | ✅ All passed |
| Voice Loop / Core              | `test_voice_loop.py` | 10     | ✅ All passed |
| Risk Assessment (parametrized) | `test_security.py`   | 10     | ✅ All passed |
| **Total**                      |                      | **60** | **✅ PASSED** |

---

## Test Breakdown

### Security Tests (21 tests)

- `rm -rf /` → **BLOCKED** ✅
- `sudo shutdown now` → **BLOCKED** ✅
- `format C:` → **BLOCKED** ✅
- `dd if=/dev/zero of=/dev/sda` → **BLOCKED** ✅
- Fork bomb `:(){ :|:& };:` → **BLOCKED** ✅
- Safe command `echo safe` → **ALLOWED** ✅
- Executor without callback → blocks dangerous ✅
- Executor with approval True → allows ✅
- Executor with approval False → blocks ✅
- Sandbox mode → blocks all without approval ✅
- Non-sandbox → allows safe commands ✅
- 10 parametrized risk classifications → all correct ✅

### Skills Integration Tests (19 tests)

- App Launcher: match open/close, no-match ✅
- File Manager: match read/mkdir, no-match ✅
- Browser: match go-to/URL, execute shortcut ✅
- Shell: match command, no-match ✅
- Dictation: match type content ✅
- Screenshot: match + execute (mocked) ✅
- Calendar: match time + execute ✅
- Email Draft: match + execute (mocked) ✅
- Notification: execute (mocked) ✅
- Web Search: local Q&A + web search (mocked) ✅

### Voice Loop / Core Tests (10 tests)

- Dispatcher: register, match, no-match, dispatch, unregister, list, disable ✅
- Sandbox: safe/moderate/dangerous assessment, execution, timeout, blocking ✅
- Pipeline: mock end-to-end (wake→STT→dispatch→TTS) ✅
- Engine: start/stop lifecycle ✅

---

## Command Used

```bash
source .venv/bin/activate && PYTHONPATH=. python -m pytest tests/ -v --tb=short
```

## Raw Output

```
60 passed in 1.28s
```
