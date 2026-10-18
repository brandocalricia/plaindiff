"""Longest common subsequence of lines, and the edit script it implies.

``dp[i][j]`` is the length of an LCS of ``a[:i]`` and ``b[:j]``.
Backtracking uses two rules, in order:

1. If the current lines are equal, take the diagonal.
2. If a deletion and an insertion preserve the same length, the
   deletion comes first in the script. A substitution is a deletion
   followed by an insertion.

The walk starts at the end of both files, and the list is reversed at
the end. A tie therefore takes the insertion during the walk, which
is what puts the deletion first in the script the caller sees.

Several alignments can share one length. The rules above pick one,
and :func:`apply_script` is how a test checks that this one was chosen.
"""

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class Op:
    kind: str
    line: str

    def __post_init__(self) -> None:
        if self.kind not in {"keep", "delete", "insert"}:
            raise ValueError(f"unknown op kind: {self.kind}")


def lcs_table(a: Sequence[str], b: Sequence[str]) -> list[list[int]]:
    """Return the (len(a)+1) by (len(b)+1) length table."""
    rows = len(a) + 1
    cols = len(b) + 1
    dp = [[0] * cols for _ in range(rows)]
    for i in range(1, rows):
        ai = a[i - 1]
        previous = dp[i - 1]
        current = dp[i]
        for j in range(1, cols):
            if ai == b[j - 1]:
                current[j] = previous[j - 1] + 1
            else:
                delete_length = previous[j]
                insert_length = current[j - 1]
                current[j] = delete_length if delete_length >= insert_length else insert_length
    return dp


def edit_script(a: Sequence[str], b: Sequence[str]) -> list[Op]:
    """Return the unique script produced by the two backtracking rules."""
    dp = lcs_table(a, b)
    i = len(a)
    j = len(b)
    reversed_ops: list[Op] = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1]:
            reversed_ops.append(Op("keep", a[i - 1]))
            i -= 1
            j -= 1
            continue
        # Strict greater, not greater-or-equal. The walk is backward, so a
        # tie takes the insertion now and the reversal puts the deletion first.
        if i > 0 and (j == 0 or dp[i - 1][j] > dp[i][j - 1]):
            reversed_ops.append(Op("delete", a[i - 1]))
            i -= 1
            continue
        reversed_ops.append(Op("insert", b[j - 1]))
        j -= 1
    reversed_ops.reverse()
    return reversed_ops


def apply_script(a: Sequence[str], script: Sequence[Op]) -> list[str]:
    """Rebuild the target file. Raise ValueError if ``script`` does not fit ``a``."""
    output: list[str] = []
    index = 0
    for op in script:
        if op.kind == "insert":
            output.append(op.line)
            continue
        if index >= len(a) or a[index] != op.line:
            raise ValueError("script does not match the source line")
        index += 1
        if op.kind == "keep":
            output.append(op.line)
    if index != len(a):
        raise ValueError("script did not consume the source")
    return output
