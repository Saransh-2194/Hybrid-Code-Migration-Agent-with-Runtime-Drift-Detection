
from analysis.static.ast_analyzer import ASTAnalyzer


def test_function_detection():
    analyzer = ASTAnalyzer()

    source = """
def calculate_discount(price, discount):
    return price - price * discount
"""

    result = analyzer.analyze_source(source)

    assert result["status"] == "success"
    assert len(result["functions"]) == 1
    assert result["functions"][0]["name"] == "calculate_discount"
    assert result["functions"][0]["arguments"] == ["price", "discount"]


def test_import_detection():
    analyzer = ASTAnalyzer()

    source = """
import os
from flask import Flask
"""

    result = analyzer.analyze_source(source)

    assert len(result["imports"]) == 2


def test_call_detection():
    analyzer = ASTAnalyzer()

    source = """
print("Hello")
"""

    result = analyzer.analyze_source(source)

    assert len(result["calls"]) == 1
    assert result["calls"][0]["function"] == "print"


def test_syntax_error_detection():
    analyzer = ASTAnalyzer()

    source = """
def calculate(
"""

    result = analyzer.analyze_source(source)

    assert result["status"] == "syntax_error"
    assert result["line"] is not None
