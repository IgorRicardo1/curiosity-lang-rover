"""
Para rodar os testes e ver se ta tudo funcionando, usa esse comando no terminal, na pasta raiz do projeto:
python -m compiler.test_compiler

Lembrete: nao roda direto clicando no play do VSCode ou 'python test_compiler.py' senao os imports relativos vao dar erro.
"""
from .emissor import emitir, formatar_hex
from .gerador_ir import GeradorIR
from .lexer import tokenizacao
from .parser import RoverParser

def teste(code):
    print("---")
    print(f"TESTANDO CODIGO: {code}")
    print("---")

    print("\n1. FASE DE ANALISE LEXICA (TOKENS):")
    print("-" * 30)
    try:
        tokens = list(tokenizacao(code))
        for t in tokens:
            print(f"Token({t.type}, '{t.value}')")
    except Exception as e:
        print(f"Erro Lexico: {e}")
        return

    print("\n2. FASE DE ANALISE SINTATICA (AST):")
    print("-" * 30)
    try:
        parser = RoverParser()
        ast = parser.parse_tokens(tokens)
        print(ast.pretty())
    except Exception as e:
        print(f"Erro Sintatico:\n{e}")
        return

    print("\n3. FASE DE GERACAO DE IR:")
    print("-" * 30)
    try:
        programa = GeradorIR().gerar(ast)
        print("Instrucoes (saltos usam indice de instrucao, nao byte):")
        for i, instr in enumerate(programa.instrucoes):
            print(f"  {i:03d} | {instr}")
        if programa.rotulos:
            print("Rotulos (referencia para explicacao):")
            for nome, indice in programa.rotulos.items():
                print(f"  {nome} -> instrucao {indice}")
    except Exception as e:
        print(f"Erro na Geracao de IR:\n{e}")
        return

    print("\n4. FASE DE EMISSAO BINARIA (.rvc):")
    print("-" * 30)
    try:
        binario = emitir(programa)
        print(f"  Tamanho: {len(binario)} bytes")
        print(formatar_hex(binario))

        print("\n5. VALIDACAO E VM (fetch-decode-execute):")
        print("-" * 30)
        from vm import executar_binario
        from vm.validador import validar_binario
        from .validador import validar_ir

        erros_ir = validar_ir(programa)
        erros_bin = validar_binario(binario)
        if erros_ir or erros_bin:
            for e in erros_ir + erros_bin:
                print(f"  ERRO: {e}")
        else:
            print("  IR e binario validos.")
            vm = executar_binario(binario)
            print(f"  {vm.resumo()}")
    except Exception as e:
        print(f"Erro:\n{e}")


if __name__ == "__main__":
    teste("AVANCA(10)")
    teste("REPITA 2 { SE OBSTACULO ENTAO { GIRA(ESQUERDA) } AVANCA(1) }")
    teste("MOVER(5)")
    teste("AVANCA()")
    teste("REP 3 { SE OBS ENTAO { GIR(ESQ) } AVA(2) }")
