from lark import Lark
import os

def get_lexer():
    grammar_path = os.path.join(os.path.dirname(__file__), 'grammar.lark')
    with open(grammar_path, 'r') as f:
        grammar = f.read()
    
    return Lark(grammar, parser='earley')

def tokenizacao(code):
    lexer_instance = get_lexer()
    return lexer_instance.lex(code)
