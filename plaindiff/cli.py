"""Command line for plaindiff."""

import sys
from pathlib import Path

from plaindiff.edit import apply_script, edit_script, lcs_table
from plaindiff.format import format_table, unified_diff
from plaindiff.io import read_lines
from plaindiff.samples import AFTER, AFTER_NAME, BEFORE, BEFORE_NAME

HELP = """\
usage:
  python -m plaindiff demo
  python -m plaindiff <old> <new>

demo prints the length table, the edit script, and the unified diff
for the four-line example in the README. Comparing two files prints
a unified diff and exits 1 when they differ, 0 when they do not.
"""


def _script_lines(script) -> str:
    return "\n".join(f"  {op.kind:<6} {op.line}" for op in script)


def run_demo() -> int:
    table = lcs_table(BEFORE, AFTER)
    script = edit_script(BEFORE, AFTER)
    rebuilt = apply_script(BEFORE, script)
    print("plaindiff: one longest-common-subsequence table")
    print()
    print("A match takes the diagonal. On a tie, delete the earlier line.")
    print()
    print(format_table(BEFORE, AFTER, table))
    print()
    print("script:")
    print(_script_lines(script))
    print()
    print(unified_diff(BEFORE_NAME, AFTER_NAME, script), end="")
    print()
    status = "ok" if rebuilt == AFTER else "FAILED"
    print(f"replay rebuilt the new file: {status}")
    return 0 if status == "ok" else 1


def compare(old: Path, new: Path) -> int:
    script = edit_script(read_lines(old), read_lines(new))
    rendered = unified_diff(f"a/{old.as_posix()}", f"b/{new.as_posix()}", script)
    if rendered:
        sys.stdout.write(rendered)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args in (["-h"], ["--help"], ["help"]):
        print(HELP, end="")
        return 0
    if args == ["demo"]:
        return run_demo()
    if len(args) != 2:
        print(HELP, end="", file=sys.stderr)
        return 2
    old = Path(args[0])
    new = Path(args[1])
    try:
        return compare(old, new)
    except (OSError, UnicodeError) as exc:
        print(f"plaindiff: {exc}", file=sys.stderr)
        return 2
