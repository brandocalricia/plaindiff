# plaindiff

A line diff that shows the table it came from.

`python -m plaindiff demo` prints a longest-common-subsequence table, the edit script that table produces, and the unified diff of that script. The script is the product. The diff is one way to print it. A test rebuilds the new file from the old file plus the script, so an alignment can have the right length and still fail.

```
python -m pytest
python -m plaindiff demo
python -m plaindiff examples/before.txt examples/after.txt
```

Python 3.11 or newer. The standard library is the only runtime dependency. `pytest` is for the tests.

## The rule

`dp[i][j]` is the length of a longest common subsequence of the first `i` lines of the old file and the first `j` lines of the new file.

Walking back from the bottom-right cell:

1. If the two lines are equal, take the diagonal. That line is kept.
2. If deleting a line and inserting a line would preserve the same length, delete. The earlier source line is consumed first, so a changed line is a deletion followed by an insertion.

Two alignments can share a length. Without rule 2 the script is not unique, and a test that only checks the length will pass for the wrong one.

The two-line tie:

```
old: a, b
new: b, a
```

Keeping `a` and keeping `b` both have length 1. The rules emit `delete a`, `keep b`, `insert a`.

## The four-line case

```
old: alpha, bravo, charlie, delta
new: alpha, charlie, delta, echo
```

```
             alpha  charlie  delta  echo
        0    0      0        0      0
alpha   0    1      1        1      1
bravo   0    1      1        1      1
charlie 0    1      2        2      2
delta   0    1      2        3      3
```

The script is `keep alpha`, `delete bravo`, `keep charlie`, `keep delta`, `insert echo`. With three lines of context that is:

```
--- a/before.txt
+++ b/after.txt
@@ -1,4 +1,4 @@
 alpha
-bravo
 charlie
 delta
+echo
```

## What the diff is not

This does not call `difflib`. `difflib` uses a different matching algorithm, so a line-by-line match with its output is not the spec.

A trailing newline is not a change. `\n`, `\r\n`, and `\r` are all line breaks, and the diff is always printed with `\n`. Counts in a hunk header are always written, including `,1` and `,0`.

There is no Myers diff, no directory walk, no move detection, and no patch command. Applying the script is `plaindiff.edit.apply_script`, and it raises if the script does not consume the old file exactly.

## Layout

| Module | What it owns |
| --- | --- |
| `plaindiff/edit.py` | The table, the script, and the replay |
| `plaindiff/format.py` | Unified diff text and the printed table |
| `plaindiff/io.py` | Reading bytes into lines |
| `plaindiff/cli.py` | `demo` and the two-file command |

Exit codes for a file comparison follow `diff`: `0` when the files match, `1` when they differ, `2` when a path cannot be read.
