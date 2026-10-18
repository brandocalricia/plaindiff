from plaindiff.io import read_lines


def test_crlf_and_lf_are_the_same_lines(tmp_path):
    lf = tmp_path / "lf.txt"
    crlf = tmp_path / "crlf.txt"
    cr = tmp_path / "cr.txt"
    lf.write_bytes(b"alpha\nbravo\n")
    crlf.write_bytes(b"alpha\r\nbravo\r\n")
    cr.write_bytes(b"alpha\rbravo\r")
    assert read_lines(lf) == read_lines(crlf) == read_lines(cr) == ["alpha", "bravo"]


def test_a_missing_trailing_newline_is_not_an_extra_line(tmp_path):
    finished = tmp_path / "finished.txt"
    bare = tmp_path / "bare.txt"
    finished.write_bytes(b"alpha\n")
    bare.write_bytes(b"alpha")
    assert read_lines(finished) == read_lines(bare) == ["alpha"]


def test_empty_file_has_no_lines(tmp_path):
    path = tmp_path / "empty.txt"
    path.write_bytes(b"")
    assert read_lines(path) == []


def test_blank_line_in_the_middle_is_kept(tmp_path):
    path = tmp_path / "blank.txt"
    path.write_bytes(b"alpha\n\nbravo\n")
    assert read_lines(path) == ["alpha", "", "bravo"]
