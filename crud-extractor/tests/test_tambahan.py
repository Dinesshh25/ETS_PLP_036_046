"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""
from crud import ast_nodes as ast
from crud.lexer import TokenType as T, tokenize
from crud.parser import parse_sql
from crud.resolver import Resolver


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


def test_bug_3_string_escaped_quote():
    """Bug 3: Dua kutip berturut-turut ('') di dalam string harus di-decode sebagai satu karakter kutip tunggal."""
    tokens = tokenize("'O''Brien' 'It''s ok'")
    assert len(tokens) == 3  # 2 string tokens + EOF
    assert tokens[0].type == T.STRING and tokens[0].value == "O'Brien"
    assert tokens[1].type == T.STRING and tokens[1].value == "It's ok"


def test_bug_7_scope_shadowing_subquery():
    """Bug 7: Pencarian scope harus dari dalam ke luar sehingga alias di subquery menutupi alias luar (shadowing)."""
    sql = "SELECT x.id FROM pelanggan x WHERE x.id IN (SELECT x.total FROM pesanan x)"
    script = parse_sql(sql)
    Resolver().resolve_script(script)
    cols = [n for n in ast.iter_nodes(script) if isinstance(n, ast.ColumnRef) and n.name == "total"]
    assert len(cols) == 1
    assert cols[0].resolved == "pesanan"


def test_bug_8_delete_scope_leak():
    """Bug 8: Scope dari statement DELETE harus dibersihkan (_pop) agar tidak bocor ke statement berikutnya."""
    sql = "DELETE FROM sesi s WHERE s.id = 1; SELECT s.id FROM pengguna u;"
    script = parse_sql(sql)
    resolver = Resolver()
    diags = resolver.resolve_script(script)
    assert resolver.scope is None
    error_msgs = [d.message for d in diags if d.level == "error"]
    assert any("alias 's' tidak terdefinisi" in m for m in error_msgs)

