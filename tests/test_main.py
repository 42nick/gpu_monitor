"""Test the main function."""

import io
import sys
import time
from pathlib import Path
from signal import SIGKILL
from unittest.mock import patch

import pytest

from gpu_monitor.main import main


@pytest.fixture
def test_data_dir() -> Path:
    """Return the path to the test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def dummy_script_path(test_data_dir: Path) -> Path:
    """Return the path to the dummy script."""
    return test_data_dir / "dummy_script.py"


def test_main() -> None:
    """Test the main function."""
    test_args = ["main.py", "--help"]
    with patch.object(sys, "argv", test_args), patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
        with pytest.raises(SystemExit) as e:
            main(args=test_args)
        assert e.value.code == 0
        output = mock_stdout.getvalue()
        assert "usage:" in output


def test_finish_with_error(dummy_script_path: Path) -> None:
    """Tests that the script properly dies after the called script raises and error."""
    start_time = time.time()
    args = [
        f"python {dummy_script_path} --iterations 5 --error_at 0",
        "--interval",
        "0.1",
    ]
    returncode = main(args)
    assert returncode != 0
    assert time.time() - start_time < 1


def test_clean_finish(dummy_script_path: Path) -> None:
    """Tests that the script properly dies after the called script raises and error."""
    start_time = time.time()
    args = [
        f"python {dummy_script_path} --iterations 0 --error_at 1",
        "--interval",
        "0.1",
    ]
    returncode = main(args)
    assert returncode == 0
    assert time.time() - start_time < 2


def test_stopping_after_timeout(dummy_script_path: Path) -> None:
    """Tests that the script properly dies after the called script raises and error."""
    start_time = time.time()
    args = [
        f"python {dummy_script_path} --iterations 3 --error_at 4",
        "--interval",
        "0.1",
        "--max_duration",
        "0.5",
    ]
    returncode = main(args)
    assert (returncode) == -SIGKILL
    assert time.time() - start_time < 2
