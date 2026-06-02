"""
ISA (Instruction Set Architecture) — opcodes compartilhados entre emissor (compiler) e VM.

Re-exporta de shared.isa para manter compatibilidade.
"""
from shared.isa import (
    OP_EMPILHA,
    OP_AVANCA,
    OP_RECUA,
    OP_GIRA_ESQUERDA,
    OP_GIRA_DIREITA,
    OP_PULA_SEM_OBS,
    OP_SALVA_REG,
    OP_DEC_PULA_NZ,
    NOMES_OP,
    Instrucao,
    codificar_linha_ir,
    decodificar,
)

__all__ = [
    "OP_EMPILHA",
    "OP_AVANCA",
    "OP_RECUA",
    "OP_GIRA_ESQUERDA",
    "OP_GIRA_DIREITA",
    "OP_PULA_SEM_OBS",
    "OP_SALVA_REG",
    "OP_DEC_PULA_NZ",
    "NOMES_OP",
    "Instrucao",
    "codificar_linha_ir",
    "decodificar",
]
