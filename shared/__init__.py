"""
Módulo shared — especificação da ISA (Instruction Set Architecture).

Contrato formal entre o compilador (que gera bytecode) e a VM (que executa).
Assim como a especificação x86 não pertence nem ao GCC nem ao processador,
a ISA é um artefato neutro que define a interface entre as duas partes.
"""
from .isa import (
    Instrucao,
    codificar_linha_ir,
    decodificar,
    NOMES_OP,
    OP_AVANCA,
    OP_DEC_PULA_NZ,
    OP_EMPILHA,
    OP_GIRA_DIREITA,
    OP_GIRA_ESQUERDA,
    OP_PULA_SEM_OBS,
    OP_RECUA,
    OP_SALVA_REG,
)
