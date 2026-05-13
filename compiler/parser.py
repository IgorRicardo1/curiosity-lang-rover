from lark import Lark
import os

class RoverParser:
    def __init__(self):
        grammar_path = os.path.join(os.path.dirname(__file__), 'grammar.lark')
        with open(grammar_path, 'r') as f:
            self.grammar = f.read()
        
        self.parser = Lark(self.grammar, start='start', parser='earley')

    def parse(self, code):
        return self.parser.parse(code)

