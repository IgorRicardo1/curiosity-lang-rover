"""
ISA (Instruction Set Architecture) — opcodes compartilhados entre emissor (compiler) e VM.
"""
import re
import struct
from dataclasses import dataclass

OP_EMPILHA = 0x01
OP_AVANCA = 0x02
OP_RECUA = 0x03
OP_GIRA_ESQUERDA = 0x04
OP_GIRA_DIREITA = 0x05
OP_PULA_SEM_OBS = 0x06
OP_SALVA_REG = 0x07
OP_DEC_PULA_NZ = 0x08

NOMES_OP = {
    OP_EMPILHA: "EMPILHA",
    OP_AVANCA: "AVANCA",
    OP_RECUA: "RECUA",
    OP_GIRA_ESQUERDA: "GIRA_ESQUERDA",
    OP_GIRA_DIREITA: "GIRA_DIREITA",
    OP_PULA_SEM_OBS: "PULA_SEM_OBS",
    OP_SALVA_REG: "SALVA_REG",
    OP_DEC_PULA_NZ: "DEC_PULA_NZ",
}

_SEM_OPERANDO_IR = {
    "AVANCA": OP_AVANCA,
    "RECUA": OP_RECUA,
    "GIRA_ESQUERDA": OP_GIRA_ESQUERDA,
    "GIRA_DIREITA": OP_GIRA_DIREITA,
}


@dataclass(frozen=True)
class Instrucao:
    opcode: int
    operandos: tuple = ()

    def mnemonico(self) -> str:
        nome = NOMES_OP.get(self.opcode, f"OP_{self.opcode:02X}")
        if not self.operandos:
            return nome
        return f"{nome} {', '.join(str(o) for o in self.operandos)}"


def _numero_reg(reg: str) -> int:
    m = re.match(r"REG(\d+)", reg.strip())
    if not m:
        raise ValueError(f"Registrador invalido: {reg}")
    return int(m.group(1))


def codificar_linha_ir(linha: str) -> bytes:
    """Uma linha do ProgramaIR -> bytes."""
    if linha in _SEM_OPERANDO_IR:
        return bytes([_SEM_OPERANDO_IR[linha]])

    if linha.startswith("EMPILHA "):
        n = int(linha.split(maxsplit=1)[1])
        if not 0 <= n <= 255:
            raise ValueError(f"EMPILHA fora do intervalo 0-255: {n}")
        return bytes([OP_EMPILHA, n])

    if linha.startswith("PULA_SEM_OBS "):
        indice = int(linha.split(maxsplit=1)[1])
        return bytes([OP_PULA_SEM_OBS]) + struct.pack("<H", indice)

    if linha.startswith("SALVA_REG "):
        reg = _numero_reg(linha.split(maxsplit=1)[1])
        return bytes([OP_SALVA_REG, reg])

    if linha.startswith("DEC_PULA_NZ "):
        resto = linha[len("DEC_PULA_NZ ") :]
        reg_str, indice_str = resto.split(", ")
        reg = _numero_reg(reg_str)
        indice = int(indice_str)
        return bytes([OP_DEC_PULA_NZ, reg]) + struct.pack("<H", indice)

    raise ValueError(f"Instrucao IR desconhecida: {linha}")


def decodificar(dados: bytes) -> list[Instrucao]:
    """Bytes .rvc -> lista de instrucoes (leitor binario)."""
    i = 0
    programa: list[Instrucao] = []
    while i < len(dados):
        op = dados[i]
        i += 1
        if op == OP_EMPILHA:
            if i >= len(dados):
                raise ValueError("EMPILHA sem operando")
            programa.append(Instrucao(op, (dados[i],)))
            i += 1
        elif op in (OP_AVANCA, OP_RECUA, OP_GIRA_ESQUERDA, OP_GIRA_DIREITA):
            programa.append(Instrucao(op))
        elif op == OP_PULA_SEM_OBS:
            if i + 2 > len(dados):
                raise ValueError("PULA_SEM_OBS incompleto")
            indice = struct.unpack_from("<H", dados, i)[0]
            i += 2
            programa.append(Instrucao(op, (indice,)))
        elif op == OP_SALVA_REG:
            if i >= len(dados):
                raise ValueError("SALVA_REG sem operando")
            programa.append(Instrucao(op, (dados[i],)))
            i += 1
        elif op == OP_DEC_PULA_NZ:
            if i + 3 > len(dados):
                raise ValueError("DEC_PULA_NZ incompleto")
            reg = dados[i]
            indice = struct.unpack_from("<H", dados, i + 1)[0]
            i += 3
            programa.append(Instrucao(op, (reg, indice)))
        else:
            raise ValueError(f"Opcode desconhecido: 0x{op:02X}")
    return programa
