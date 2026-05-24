"""
Small debug logger for backend request and LLM traces.
"""

from datetime import datetime
from pathlib import Path


LOG_PATH = Path(__file__).resolve().parents[1] / "debug.log"


def debug_log(message: str) -> None:
    """
    Print to stdout and append to nova-backend/debug.log.
    """
    timestamped = f"[{datetime.now().isoformat(timespec='seconds')}] {message}"
    print(timestamped, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(timestamped)
        if not timestamped.endswith("\n"):
            log_file.write("\n")
