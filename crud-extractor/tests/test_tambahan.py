"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""
import pytest
from crud import ast_nodes as ast
from crud.analyzer import analyze_statement
from crud.lexer import LexError, TokenType as T, tokenize
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


# LIMA TEST KASUS TEPI (EDGE CASES) DENGAN KOMENTAR RISIKO

def test_edge_case_1_unclosed_block_comment():
    """Kasus tepi 1: Komentar blok yang tidak ditutup sampai akhir file (EOF).
    Risiko: Scanner berisiko loop tak hingga atau crash jika pengecekan EOF tidak
    ketat saat mencari penutup '*/'. Menurut SPESIFIKASI.md 2.3, harus melempar LexError.
    """
    with pytest.raises(LexError) as exc_info:
        tokenize("SELECT 1; /* komentar yang lupa ditutup")
    assert "tidak ditutup" in str(exc_info.value)


def test_edge_case_2_consecutive_escaped_quotes_only():
    """Kasus tepi 2: String yang hanya berisi escape kutip ganda berturut-turut ('''' mewakili satu karakter kutip tunggal).
    Risiko: Rentan error off-by-one pada lookahead _peek(). Jika scanner salah mengonsumsi karakter kutip
    penutup sebagai bagian dari escape, string akan dianggap tidak ditutup (unclosed string LexError).
    """
    tokens = tokenize("''''")
    assert len(tokens) == 2  # STRING + EOF
    assert tokens[0].type == T.STRING
    assert tokens[0].value == "'"


def test_edge_case_3_chained_and_or_precedence():
    """Kasus tepi 3: Rantai logika kompleks kombinasi AND dan OR (A AND B OR C AND D).
    Risiko: Struktur pohon AST berisiko salah asosiatif jika pemanggilan rekursif grammar
    tidak mengikat AND lebih kuat di kedua sisi percabangan OR.
    """
    script = parse_sql("SELECT * FROM t WHERE a = 1 AND b = 2 OR c = 3 AND d = 4;")
    assert script.errors == []
    where = script.statements[0].where
    assert isinstance(where, ast.BinaryOp) and where.op == "OR"
    assert isinstance(where.left, ast.BinaryOp) and where.left.op == "AND"
    assert isinstance(where.right, ast.BinaryOp) and where.right.op == "AND"


def test_edge_case_4_unqualified_column_ambiguous():
    """Kasus tepi 4: Resolusi kolom tanpa qualifier saat query membaca lebih dari satu tabel (multi-table FROM).
    Risiko: Tanpa skema database, tool tidak boleh menebak asal tabel sembarangan. Menurut SPESIFIKASI.md 4.3,
    resolver wajib menghasilkan warning ambiguitas dan nilai ColumnRef.resolved harus tetap None.
    """
    script = parse_sql("SELECT id FROM pelanggan p, pesanan o;")
    resolver = Resolver()
    diags = resolver.resolve_script(script)
    warnings = [d.message for d in diags if d.level == "warning"]
    assert any("ambigu tanpa skema" in m for m in warnings)
    col = [n for n in ast.iter_nodes(script) if isinstance(n, ast.ColumnRef)][0]
    assert col.resolved is None


def test_edge_case_5_multi_level_subquery_shadowing():
    """Kasus tepi 5: Shadowing nama alias yang sama di tiga level hierarki subquery bersarang.
    Risiko: Struktur resolver berbasis lexical stack rentan mengalami kebocoran scope atau salah
    referensi parent jika penelusuran AST dari scope terdalam ke scope luar tidak terisolasi sempurna.
    """
    sql = (
        "SELECT t.a FROM x t WHERE t.id IN ("
        "  SELECT t.b FROM y t WHERE t.id IN ("
        "    SELECT t.c FROM z t"
        "  )"
        ")"
    )
    script = parse_sql(sql)
    Resolver().resolve_script(script)
    cols = [n for n in ast.iter_nodes(script) if isinstance(n, ast.ColumnRef)]
    assert cols[0].resolved == "x"
    assert cols[2].resolved == "y"
    assert cols[4].resolved == "z"
