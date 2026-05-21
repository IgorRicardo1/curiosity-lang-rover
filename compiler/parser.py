"""
Análise sintática — monta a AST a partir de tokens produzidos pelo lexer.
"""
from lark import Lark
from lark.lexer import Lexer

from .lexer import load_grammar

_token_parser = None


class TokenStreamLexer(Lexer):
    def __init__(self, lexer_conf=None):
        pass

    def lex(self, stream):
        yield from stream


def get_token_parser() -> Lark:
    global _token_parser
    if _token_parser is None:
        _token_parser = Lark(
            load_grammar(),
            start="start",
            parser="earley",
            lexer=TokenStreamLexer,
        )
    return _token_parser


class RoverParser:
    def __init__(self):
        self._parser = get_token_parser()

    def parse_tokens(self, tokens):
        """Tokens (saída do lexer) → AST."""
        return self._parser.parse(tokens)
