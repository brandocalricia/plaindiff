"""Render an edit script as a unified diff.

Counts are always written, including ``,1`` and ``,0``. A missing final
newline in either file is not represented: the script is lines, not bytes.
Identical inputs produce an empty string, with no file headers.
"""

from dataclasses import dataclass
from typing import Sequence

from plaindiff.edit import Op


@dataclass(frozen=True)
class _Record:
    tag: str
    line: str
    old_index: int | None
    new_index: int | None
    old_before: int
    new_before: int


def _records(script: Sequence[Op]) -> list[_Record]:
    records: list[_Record] = []
    old_count = 0
    new_count = 0
    for op in script:
        if op.kind == "keep":
            records.append(_Record(" ", op.line, old_count, new_count, old_count, new_count))
            old_count += 1
            new_count += 1
        elif op.kind == "delete":
            records.append(_Record("-", op.line, old_count, None, old_count, new_count))
            old_count += 1
        elif op.kind == "insert":
            records.append(_Record("+", op.line, None, new_count, old_count, new_count))
            new_count += 1
        else:
            raise ValueError(f"unknown op kind: {op.kind}")
    return records


def _range(start: int, length: int) -> str:
    """Format one side of a hunk header.

    ``start`` is the 0-based index of the first line. A zero-length range
    uses ``start`` itself, which is the number of lines before an insertion
    or a deletion that contributes nothing to that side. That is why an
    insert at the top of an empty file is ``-0,0``.
    """
    if length == 0:
        return f"{start},0"
    return f"{start + 1},{length}"


def _hunks(records: Sequence[_Record], context: int) -> list[tuple[int, int]]:
    change_indexes = [index for index, record in enumerate(records) if record.tag != " "]
    ranges: list[tuple[int, int]] = []
    for index in change_indexes:
        start = max(0, index - context)
        end = min(len(records), index + context + 1)
        if ranges and start <= ranges[-1][1]:
            ranges[-1] = (ranges[-1][0], max(ranges[-1][1], end))
        else:
            ranges.append((start, end))
    return ranges


def unified_diff(a_name: str, b_name: str, script: Sequence[Op], context: int = 3) -> str:
    """Return a unified diff, or ``""`` when ``script`` has no changes."""
    if context < 0:
        raise ValueError("context must be zero or greater")
    records = _records(script)
    ranges = _hunks(records, context)
    if not ranges:
        return ""
    lines = [f"--- {a_name}", f"+++ {b_name}"]
    for start, end in ranges:
        hunk = records[start:end]
        old_indexes = [record.old_index for record in hunk if record.old_index is not None]
        new_indexes = [record.new_index for record in hunk if record.new_index is not None]
        if old_indexes:
            old_header = _range(old_indexes[0], len(old_indexes))
        else:
            old_header = _range(hunk[0].old_before, 0)
        if new_indexes:
            new_header = _range(new_indexes[0], len(new_indexes))
        else:
            new_header = _range(hunk[0].new_before, 0)
        lines.append(f"@@ -{old_header} +{new_header} @@")
        lines.extend(f"{record.tag}{record.line}" for record in hunk)
    return "\n".join(lines) + "\n"


def format_table(a: Sequence[str], b: Sequence[str], dp: Sequence[Sequence[int]]) -> str:
    """Render ``dp`` with ``a`` as row labels and ``b`` as column labels."""
    column_labels = [""] + list(b)
    row_labels = [""] + list(a)
    width = 1
    for label in column_labels + row_labels:
        width = max(width, len(label))
    width = max(width, len(str(dp[-1][-1])))
    header = " ".join(label.rjust(width) for label in column_labels)
    lines = [header]
    for label, row in zip(row_labels, dp):
        cells = [label.rjust(width)] + [str(value).rjust(width) for value in row]
        lines.append(" ".join(cells))
    return "\n".join(lines)
