from crud.parser import parse_sql

def test_and_or():
    script = parse_sql("SELECT id FROM t WHERE a = 1 OR b = 2 AND c = 3;")

    assert script.errors == [], script.errors
    assert script.statements[0].where_clause is not None