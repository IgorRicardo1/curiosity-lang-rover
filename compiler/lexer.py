"""
Análise léxica — converte texto-fonte em tokens.
"""
import os

from lark import Lark

_lark_instance = None


def load_grammar() -> str:
    grammar_path = os.path.join(os.path.dirname(__file__), "grammar.lark")
    with open(grammar_path, encoding="utf-8") as f:
        return f.read()


def get_lark() -> Lark:
    global _lark_instance
    if _lark_instance is None:
        _lark_instance = Lark(load_grammar(), start="start", parser="earley")
    return _lark_instance


def tokenizacao(code: str):
    """Texto-fonte → stream de tokens."""
    return get_lark().lex(code)
