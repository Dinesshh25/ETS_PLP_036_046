from crud.parser import parse_sql

def test_left_outer_join():
    script = parse_sql("SELECT * FROM a LEFT OUTER JOIN b ON a.id = b.id;")

    assert script.errors == [], script.errors
    assert script.statements[0].joins[0].kind == "LEFT"