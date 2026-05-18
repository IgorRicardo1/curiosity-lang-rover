"""
=============================================================================
PIPELINE DO COMPILADOR ROVER
=============================================================================

Este script testa as três primeiras fases do nosso compilador:
1. ANÁLISE LÉXICA (Lexer): 
   Responsável por ler o texto bruto e quebrá-lo em "Tokens" (palavras, 
   números e símbolos). Ele usa as regras definidas em maiúsculas no 
   `grammar.lark` (ex: AVANCA, NUMBER, LPAR).

2. ANÁLISE SINTÁTICA (Parser): 
   Responsável por pegar a lista de Tokens gerada pelo Lexer e organizá-los 
   em uma Árvore de Sintaxe Abstrata (AST), validando se as ordens fazem 
   sentido gramaticalmente. Ele usa as regras em minúsculas do 
   `grammar.lark` (ex: instrucao, movimento, controle).

3. GERAÇÃO DE BYTECODE (Codegen):
   Responsável por visitar a AST e gerar as instruções lineares de baixo 
   nível para a nossa Máquina de Pilha (ex: EMPILHA, AVANCA, PULA_SEM_OBS).

O fluxo completo é: 
Código Fonte (.rover) -> [ Lexer ] -> Tokens -> [ Parser ] -> AST -> [ Bytecode_Gen ] -> Instruções
=============================================================================
"""
from lexer import tokenizacao
from parser import RoverParser
from bytecode_gen import BytecodeGenerator


def teste(code):
    print("=" * 50)
    print(f"TESTANDO CÓDIGO: {code}")
    print("=" * 50)
    #Lexer
    print("\n1. FASE DE ANÁLISE LÉXICA (TOKENS):")
    print("-" * 30)
    try:
        tokens = list(tokenizacao(code))
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
        return
    # Bytecode
    print("\n3. FASE DE GERAÇÃO DE BYTECODE:")
    print("-" * 30)
    try:
        gerador = BytecodeGenerator()
        bytecode = gerador.gerar(ast)
        for i, instr in enumerate(bytecode):
            print(f"{i:03d} | {instr}")
    except Exception as e:
        print(f"Erro na Geração de Bytecode:\n{e}")

if __name__ == "__main__":

    # Teste 1: Comando Simples
    teste("AVANCA(10)")
    
    # Teste 2: Loop e Condicional
    teste("REPITA 2 { SE OBSTACULO ENTAO { GIRA(ESQUERDA) } AVANCA(1) }")
    
    # Teste 3: Erro Proposital
    teste("MOVER(5)") # 'MOVER' não existe na gramática
    
    # Teste 4: Usando abreviações
    teste("REP 3 { SE OBS ENTAO { GIR(ESQ) } AVA(2) }")
