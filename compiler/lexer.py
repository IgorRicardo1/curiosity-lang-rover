from lark import Lark

def get_lexer():
    with open('compiler/grammar.lark', 'r') as f:
        grammar = f.read()
    
    return Lark(grammar, parser='earley')

def tokenize(code):
    lexer_instance = get_lexer()
    return lexer_instance.lex(code)
