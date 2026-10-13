import pytest
from locspoof.core.exceptions import LocSpoofError
from locspoof.utils.process import safe_run


def test_safe_run_success():
    res = safe_run(["echo", "cybersecurity_testing"])
    assert res.success is True
    assert res.stdout == "cybersecurity_testing"


def test_safe_run_nonexistent_executable():
    with pytest.raises(LocSpoofError) as exc_info:
        safe_run(["non_existent_binary_xyz_123"])
    assert exc_info.value.exit_code == 3
    assert "Executable 'non_existent_binary_xyz_123' not found" in exc_info.value.message


def test_safe_run_blocks_shell_operators():
    # Because shell=False, shell operators like ';' or '&&' are treated as literal arguments
    res = safe_run(["echo", "hello; whoami"])
    assert res.stdout == "hello; whoami"
