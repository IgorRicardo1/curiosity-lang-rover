"""
IR (Intermediate Representation) — saída do codegen.
"""
from dataclasses import dataclass

@dataclass
class ProgramaIR:
    instrucoes: list[str]
    rotulos: dict[str, int]
