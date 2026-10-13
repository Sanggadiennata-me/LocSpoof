"""
Safe, hardened subprocess execution utility.
Strictly avoids shell=True and enforces argument validation.
"""

import shutil
import subprocess
from typing import List, Optional, Tuple

from locspoof.core.exceptions import LocSpoofError


class ProcessResult:
    def __init__(self, stdout: str, stderr: str, returncode: int):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

    @property
    def success(self) -> bool:
        return self.returncode == 0


import os


def find_executable(name: str) -> Optional[str]:
    """Find absolute path of an executable in system PATH or standard SDK locations."""
    # 1. Standard system PATH
    found = shutil.which(name)
    if found:
        return found

    # 2. Local platform-tools directories
    candidates = [
        os.path.expanduser(f"~/.local/share/locspoof/platform-tools/{name}"),
        os.path.expanduser(f"~/Android/Sdk/platform-tools/{name}"),
        os.path.expanduser(f"~/Library/Android/sdk/platform-tools/{name}"),
        os.path.expanduser(f"/usr/local/bin/{name}"),
    ]
    for p in candidates:
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p

    return None


def safe_run(
    cmd: List[str],
    timeout: float = 15.0,
    check: bool = False,
    cwd: Optional[str] = None,
) -> ProcessResult:
    """
    Execute an external command safely without shell expansion.
    
    Args:
        cmd: List of command arguments. First item is the binary name or path.
        timeout: Execution timeout in seconds.
        check: Whether to raise LocSpoofError on non-zero exit code.
        cwd: Working directory.
    
    Returns:
        ProcessResult containing stdout, stderr, and returncode.
    """
    executable = cmd[0]
    resolved = find_executable(executable)
    if not resolved and not executable.startswith(("/", "./", "../")):
        raise LocSpoofError(
            message=f"Executable '{executable}' not found.",
            detail=f"The command '{executable}' is not available in system PATH or Android SDK locations.",
            suggestion=f"Please verify that '{executable}' is installed.",
            exit_code=3,
        )
    if resolved:
        cmd[0] = resolved

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            cwd=cwd,
            shell=False,  # Enforce NO shell
        )
        result = ProcessResult(
            stdout=proc.stdout.strip(),
            stderr=proc.stderr.strip(),
            returncode=proc.returncode,
        )
        if check and not result.success:
            raise LocSpoofError(
                message=f"Command '{executable}' failed with exit code {result.returncode}.",
                detail=result.stderr or result.stdout,
                suggestion=f"Check the parameters or environment for '{executable}'.",
                exit_code=1,
            )
        return result
    except subprocess.TimeoutExpired as exc:
        raise LocSpoofError(
            message=f"Command '{executable}' timed out after {timeout} seconds.",
            detail=str(exc),
            suggestion="Check network or device connectivity.",
            exit_code=1,
        ) from exc
    except OSError as exc:
        raise LocSpoofError(
            message=f"Failed to execute command '{executable}'.",
            detail=str(exc),
            suggestion="Verify execution permissions and binary integrity.",
            exit_code=1,
        ) from exc
