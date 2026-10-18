"""Read a text file as lines.

Only ``\\n``, ``\\r\\n``, and ``\\r`` are line breaks. A trailing break does
not create an extra empty line, so a file that ends in a newline and a file
that does not compare equal when their lines match. This is a line diff,
not a byte diff.
"""

from pathlib import Path


def read_lines(path: Path) -> list[str]:
    text = Path(path).read_bytes().decode("utf-8")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if text == "":
        return []
    if text.endswith("\n"):
        text = text[:-1]
    return text.split("\n")
