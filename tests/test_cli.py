import subprocess
import sys
from pathlib import Path

from plaindiff.cli import main
from plaindiff.samples import AFTER, BEFORE

ROOT = Path(__file__).resolve().parents[1]


def test_demo_exits_zero_and_shows_the_table_and_the_replay(capsys):
    assert main(["demo"]) == 0
    output = capsys.readouterr().out
    assert "bravo" in output
    assert "-bravo" in output
    assert "+echo" in output
    assert "replay rebuilt the new file: ok" in output


def test_compare_exits_one_and_prints_a_diff(tmp_path, capsys):
    old = tmp_path / "old.txt"
    new = tmp_path / "new.txt"
    old.write_bytes(("\n".join(BEFORE) + "\n").encode())
    new.write_bytes(("\n".join(AFTER) + "\n").encode())
    assert main([str(old), str(new)]) == 1
    output = capsys.readouterr().out
    assert output.startswith("--- a/")
    assert "-bravo\n" in output
    assert "+echo\n" in output


def test_equal_files_exit_zero_with_no_output(tmp_path, capsys):
    old = tmp_path / "old.txt"
    new = tmp_path / "new.txt"
    old.write_bytes(b"alpha\r\n")
    new.write_bytes(b"alpha\n")
    assert main([str(old), str(new)]) == 0
    assert capsys.readouterr().out == ""


def test_missing_file_exits_two(tmp_path, capsys):
    assert main([str(tmp_path / "missing.txt"), str(tmp_path / "also.txt")]) == 2
    assert "plaindiff:" in capsys.readouterr().err


def test_help_and_usage():
    assert main(["--help"]) == 0
    assert main([]) == 2


def test_module_entrypoint_runs_the_demo():
    completed = subprocess.run(
        [sys.executable, "-m", "plaindiff", "demo"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    assert "replay rebuilt the new file: ok" in completed.stdout


def test_checked_in_examples_match_the_sample():
    before = (ROOT / "examples" / "before.txt").read_bytes()
    after = (ROOT / "examples" / "after.txt").read_bytes()
    assert before == ("\n".join(BEFORE) + "\n").encode()
    assert after == ("\n".join(AFTER) + "\n").encode()
