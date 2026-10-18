import itertools
import random

import pytest

from plaindiff.edit import Op, apply_script, edit_script, lcs_table
from plaindiff.samples import AFTER, BEFORE, TIE_AFTER, TIE_BEFORE


def slow_lcs_length(a, b):
    cache = {}

    def solve(i, j):
        if i == 0 or j == 0:
            return 0
        key = (i, j)
        if key in cache:
            return cache[key]
        if a[i - 1] == b[j - 1]:
            result = 1 + solve(i - 1, j - 1)
        else:
            result = max(solve(i - 1, j), solve(i, j - 1))
        cache[key] = result
        return result

    return solve(len(a), len(b))


def test_demo_script_is_the_one_from_the_readme():
    script = edit_script(BEFORE, AFTER)
    assert [(op.kind, op.line) for op in script] == [
        ("keep", "alpha"),
        ("delete", "bravo"),
        ("keep", "charlie"),
        ("keep", "delta"),
        ("insert", "echo"),
    ]
    assert lcs_table(BEFORE, AFTER)[-1][-1] == 3


def test_tie_deletes_the_earlier_line_first():
    script = edit_script(TIE_BEFORE, TIE_AFTER)
    assert [(op.kind, op.line) for op in script] == [
        ("delete", "a"),
        ("keep", "b"),
        ("insert", "a"),
    ]


def test_substitution_is_delete_then_insert():
    script = edit_script(["old"], ["new"])
    assert [(op.kind, op.line) for op in script] == [
        ("delete", "old"),
        ("insert", "new"),
    ]


def test_apply_rejects_a_script_that_does_not_fit():
    with pytest.raises(ValueError):
        apply_script(["alpha"], [Op("keep", "beta")])
    with pytest.raises(ValueError):
        apply_script(["alpha", "bravo"], [Op("keep", "alpha")])


def test_every_short_pair_replays_and_matches_a_slow_lcs():
    lists = [[]]
    for length in range(1, 5):
        lists.extend(list(item) for item in itertools.product(["a", "b"], repeat=length))
    for left, right in itertools.product(lists, repeat=2):
        table = lcs_table(left, right)
        script = edit_script(left, right)
        assert apply_script(left, script) == right
        keeps = [op.line for op in script if op.kind == "keep"]
        assert len(keeps) == table[-1][-1] == slow_lcs_length(left, right)
        assert _is_subsequence(keeps, left)
        assert _is_subsequence(keeps, right)


def test_seeded_random_pairs_replay():
    rng = random.Random(0)
    alphabet = ["red", "green", "blue", ""]
    for _ in range(200):
        left = [rng.choice(alphabet) for _ in range(rng.randint(0, 12))]
        right = [rng.choice(alphabet) for _ in range(rng.randint(0, 12))]
        script = edit_script(left, right)
        assert apply_script(left, script) == right
        assert len([op for op in script if op.kind == "keep"]) == lcs_table(left, right)[-1][-1]


def _is_subsequence(needle, haystack):
    index = 0
    for item in haystack:
        if index < len(needle) and item == needle[index]:
            index += 1
    return index == len(needle)
