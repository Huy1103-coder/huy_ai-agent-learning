# 这是给 pytest 看的，里面只有断言

def test_addition():
    assert 1 + 1 == 2

def test_string_upper():
    assert "hello".upper() == "HELLO"

def test_list_contains():
    fruits = ["apple", "banana", "cherry"]
    assert "banana" in fruits

def test_will_fail():
    """这个故意写错,看 pytest 怎么报错"""
    assert 1 + 1 == 3   # ← 这是错的

