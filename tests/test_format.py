from plaindiff.edit import Op, edit_script
from plaindiff.format import format_table, unified_diff
from plaindiff.samples import AFTER, AFTER_NAME, BEFORE, BEFORE_NAME


def test_identical_files_have_no_diff_text():
    script = edit_script(["alpha"], ["alpha"])
    assert unified_diff("a/x", "b/x", script) == ""


def test_demo_diff_matches_the_hand_written_hunk():
    script = edit_script(BEFORE, AFTER)
    assert unified_diff(BEFORE_NAME, AFTER_NAME, script) == (
        "--- a/before.txt\n"
        "+++ b/after.txt\n"
        "@@ -1,4 +1,4 @@\n"
        " alpha\n"
        "-bravo\n"
        " charlie\n"
        " delta\n"
        "+echo\n"
    )


def test_context_zero_splits_the_demo_into_two_hunks():
    script = edit_script(BEFORE, AFTER)
    assert unified_diff(BEFORE_NAME, AFTER_NAME, script, context=0) == (
        "--- a/before.txt\n"
        "+++ b/after.txt\n"
        "@@ -2,1 +1,0 @@\n"
        "-bravo\n"
        "@@ -4,0 +4,1 @@\n"
        "+echo\n"
    )


def test_insert_into_an_empty_file():
    script = [Op("insert", "hello")]
    assert unified_diff("a/empty", "b/empty", script, context=0) == (
        "--- a/empty\n"
        "+++ b/empty\n"
        "@@ -0,0 +1,1 @@\n"
        "+hello\n"
    )


def test_delete_leaves_an_empty_file():
    script = [Op("delete", "hello")]
    assert unified_diff("a/gone", "b/gone", script, context=0) == (
        "--- a/gone\n"
        "+++ b/gone\n"
        "@@ -1,1 +0,0 @@\n"
        "-hello\n"
    )


def test_table_labels_the_demo_rows_and_columns():
    from plaindiff.edit import lcs_table

    rendered = format_table(BEFORE, AFTER, lcs_table(BEFORE, AFTER))
    rows = rendered.splitlines()
    assert "alpha" in rows[0]
    assert rows[2].split()[0] == "alpha"
    assert rows[-1].split()[-1] == "3"


def test_negative_context_is_rejected():
    import pytest

    with pytest.raises(ValueError):
        unified_diff("a", "b", [], context=-1)
