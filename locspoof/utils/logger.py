"""
Structured logging system for locspoof.
Supports quiet, normal, verbose, and debug verbosity levels with sensitive data sanitization.
"""

import logging
import re
from typing import Any

from rich.console import Console
from rich.logging import RichHandler

console = Console(stderr=True)

# Regex to redact potential auth/passwords in URLs or logs
SENSITIVE_PATTERNS = [
    re.compile(r"(://[^:]+:)([^@]+)(@)"),  # URL credentials user:pass@host
    re.compile(r"(--password[=\s]+)(\S+)", re.IGNORECASE),
    re.compile(r"(bearer\s+)([a-zA-Z0-9_\-\.]+)", re.IGNORECASE),
]


def sanitize_log_message(msg: str) -> str:
    """Mask sensitive tokens, passwords, and credentials from log output."""
    if not isinstance(msg, str):
        return msg
    sanitized = msg
    for pattern in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(r"\g<1>******\g<3>" if pattern.groups == 3 else r"\g<1>******", sanitized)
    return sanitized


class SanitizedRichHandler(RichHandler):
    """Custom Rich handler that masks sensitive strings."""

    def emit(self, record: logging.LogRecord) -> None:
        if isinstance(record.msg, str):
            record.msg = sanitize_log_message(record.msg)
        super().emit(record)


def setup_logger(verbosity: str = "normal") -> logging.Logger:
    """
    Setup the global locspoof logger.
    
    Levels:
        quiet: ERROR only
        normal: INFO, WARNING, ERROR
        verbose: DEBUG details for providers
        debug: Full tracing, internal state
    """
    logger = logging.getLogger("locspoof")
    logger.handlers.clear()
    logger.propagate = False

    level_map = {
        "quiet": logging.ERROR,
        "normal": logging.INFO,
        "verbose": logging.DEBUG,
        "debug": logging.DEBUG,
    }
    log_level = level_map.get(verbosity.lower(), logging.INFO)
    logger.setLevel(log_level)

    handler = SanitizedRichHandler(
        console=console,
        show_time=log_level == logging.DEBUG,
        show_path=log_level == logging.DEBUG,
        rich_tracebacks=True,
    )
    logger.addHandler(handler)
    return logger


# Default logger instance
logger = setup_logger("normal")
