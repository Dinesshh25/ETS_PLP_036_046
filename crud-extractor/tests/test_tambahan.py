"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""
from crud.lexer import TokenType as T, tokenize


def test_bug_1_keyword_case_insensitive():
    """Bug 1: Keyword huruf kecil/campuran harus dikenali sebagai KEYWORD dan diubah ke UPPERCASE."""
    tokens = tokenize("select DISTINCT id FrOm pelanggan where aktif = 1")
    keywords = [(t.value, t.type) for t in tokens if t.type == T.KEYWORD]
    assert keywords == [
        ("SELECT", T.KEYWORD),
        ("DISTINCT", T.KEYWORD),
        ("FROM", T.KEYWORD),
        ("WHERE", T.KEYWORD),
    ]


def test_bug_2_operator_not_equal():
    """Bug 2: Operator '<>' harus di-scan sebagai satu token OP '<>', bukan terbelah '<' dan '>'."""
    tokens = tokenize("catatan <> 'rahasia'")
    op_tokens = [t for t in tokens if t.type == T.OP]
    assert len(op_tokens) == 1
    assert op_tokens[0].value == "<>"


