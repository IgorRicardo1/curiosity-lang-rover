"""
Módulo compiler — Análise léxica/sintática e geração de IR/binário.
"""
from .emissor import emitir, formatar_hex, salvar_rvc
from .gerador_ir import GeradorIR
from .ir import ProgramaIR
from .lexer import tokenizacao
from .parser import RoverParser
from .validador import exigir_ir_valido


def compilar(code: str) -> ProgramaIR:
    try:
        tokens = list(tokenizacao(code))
    except Exception as e:
        raise ValueError(f"Erro Lexico: {e}")

    try:
        ast = RoverParser().parse_tokens(tokens)
    except Exception as e:
        raise ValueError(f"Erro Sintatico: {e}")
    programa = GeradorIR().gerar(ast)
    exigir_ir_valido(programa)
    return programa


def para_binario(ir: ProgramaIR) -> bytes:
    """IR já compilado → bytes .rvc."""
    exigir_ir_valido(ir)
    return emitir(ir)
