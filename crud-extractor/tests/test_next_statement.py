from crud.lexer import tokenize
from crud.parser import parse_sql
from crud.pipeline import analyze_source
from crud.analyzer import analyze_statement


def test_next_statement():
    sql = "SELECT department_id FROM departments EXCEPT SELECT department_id FROM employees;"
    res = analyze_source(sql)
    
    assert len(res.parse_errors) == 1
    assert len(res.statements) == 1 
    assert res.statements[0].table_ref.name == "t2"