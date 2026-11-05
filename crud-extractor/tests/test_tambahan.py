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

