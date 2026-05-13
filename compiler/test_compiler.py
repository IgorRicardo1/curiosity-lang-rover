"""
=============================================================================
PIPELINE DO COMPILADOR ROVER
=============================================================================

Este script testa as duas primeiras fases do nosso compilador:
1. ANÁLISE LÉXICA (Lexer): 
   Responsável por ler o texto bruto e quebrá-lo em "Tokens" (palavras, 
   números e símbolos). Ele usa as regras definidas em maiúsculas no 
   `grammar.lark` (ex: AVANCA, NUMBER, LPAR).

2. ANÁLISE SINTÁTICA (Parser): 
   Responsável por pegar a lista de Tokens gerada pelo Lexer e organizá-los 
   em uma Árvore de Sintaxe Abstrata (AST), validando se as ordens fazem 
   sentido gramaticalmente. Ele usa as regras em minúsculas do 
   `grammar.lark` (ex: instrucao, movimento, controle).

O fluxo completo é: 
Código Fonte (.rover) -> [ Lexer ] -> Tokens -> [ Parser ] -> AST (Árvore)
=============================================================================
"""
from lexer import tokenize
from parser import RoverParser


def test_full_pipeline(code):
    print("=" * 50)
    print(f"TESTANDO CÓDIGO: {code}")
    print("=" * 50)
    #Lexer
    print("\n1. FASE DE ANÁLISE LÉXICA (TOKENS):")
    print("-" * 30)
    try:
        tokens = list(tokenize(code))
        for t in tokens:
            print(f"[{t.type:.<12}] -> '{t.value}'")
    except Exception as e:
        print(f"Erro Léxico: {e}")
        return
    #parser
    print("\n2. FASE DE ANÁLISE SINTÁTICA (AST):")
    print("-" * 30)
    try:
        parser = RoverParser()
        ast = parser.parse(code)
        print(ast.pretty())
    except Exception as e:
        print(f"Erro Sintático:\n{e}")

if __name__ == "__main__":
    # Teste 1: Comando Simples
    test_full_pipeline("AVANCA(10)")
    
    # Teste 2: Loop e Condicional
    test_full_pipeline("REPITA 2 { SE OBSTACULO ENTAO { GIRA(ESQUERDA) } AVANCA(1) }")
    
    # Teste 3: Erro Proposital
    test_full_pipeline("MOVER(5)") # 'MOVER' não existe na gramática
    
    # Teste 4: Usando abreviações (novo recurso!)
    test_full_pipeline("REP 3 { SE OBS ENTAO { GIR(ESQ) } AVA(2) }")
