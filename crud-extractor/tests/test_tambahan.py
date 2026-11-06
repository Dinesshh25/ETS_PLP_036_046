"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""
from crud import ast_nodes as ast
from crud.analyzer import analyze_statement
from crud.lexer import TokenType as T, tokenize
from crud.parser import parse_sql
from crud.pipeline import analyze_source
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

def test_left_outer_join():
    script = parse_sql("SELECT * FROM a LEFT OUTER JOIN b ON a.id = b.id;")

    assert script.errors == [], script.errors
    assert script.statements[0].joins[0].kind == "LEFT"


def test_and_or():
    script = parse_sql("SELECT id FROM t WHERE a = 1 OR b = 2 AND c = 3;")

    assert script.errors == [], script.errors
    where = script.statements[0].where
    assert isinstance(where, ast.BinaryOp) and where.op == "OR"
    assert isinstance(where.right, ast.BinaryOp) and where.right.op == "AND"

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


def test_bug9_update_subquery_read():
    """Subquery di WHERE UPDATE membaca tabelnya, bukan meng-update tabel tersebut."""
    sql = "UPDATE pelanggan SET level = 1 WHERE id IN (SELECT id FROM pesanan);"
    script = parse_sql(sql)

    assert script.errors == [], script.errors
    matrix = analyze_statement(script.statements[0])

    assert matrix["pelanggan"] == {"U"}
    assert matrix["pesanan"] == {"R"}


def test_next_statement():
    sql = "SELECT department_id FROM departments EXCEPT SELECT department_id FROM employees;"
    res = analyze_source(sql)

    assert len(res.parse_errors) == 1
    assert len(res.statements) == 1
    assert res.statements[0].tables == {"employees": "R"}