"""Validacao de IR e de programa binario decodificado."""
from compiler.ir import ProgramaIR

from .isa import Instrucao, NOMES_OP, decodificar

_INSTRUCOES_CONHECIDAS = {
    "EMPILHA",
    "AVANCA",
    "RECUA",
    "GIRA_ESQUERDA",
    "GIRA_DIREITA",
    "PULA_SEM_OBS",
    "SALVA_REG",
    "DEC_PULA_NZ",
}


def validar_ir(programa: ProgramaIR) -> list[str]:
    erros = []
    n = len(programa.instrucoes)

    if n == 0:
        return erros

    for i, linha in enumerate(programa.instrucoes):
        nome = linha.split()[0] if linha else ""
        if nome not in _INSTRUCOES_CONHECIDAS:
            erros.append(f"Instrucao {i}: desconhecida '{linha}'")
            continue

        if linha.startswith("PULA_SEM_OBS ") or linha.startswith("DEC_PULA_NZ "):
            try:
                if linha.startswith("PULA_SEM_OBS "):
                    idx = int(linha.split(maxsplit=1)[1])
                else:
                    idx = int(linha.split(", ")[1])
                if not 0 <= idx < n:
                    erros.append(
                        f"Instrucao {i}: salto para indice {idx} fora de [0, {n - 1}]"
                    )
            except (IndexError, ValueError):
                erros.append(f"Instrucao {i}: operando de salto invalido")

    return erros


def validar_instrucoes(programa: list[Instrucao]) -> list[str]:
    erros = []
    n = len(programa)

    if n == 0:
        return erros

    for i, ins in enumerate(programa):
        if ins.opcode not in NOMES_OP:
            erros.append(f"Instrucao {i}: opcode invalido 0x{ins.opcode:02X}")

        if ins.opcode in (0x06, 0x08) and len(ins.operandos) >= 1:
            idx = ins.operandos[-1]
            if not 0 <= idx < n:
                erros.append(
                    f"Instrucao {i}: salto para indice {idx} fora de [0, {n - 1}]"
                )

    return erros


def validar_binario(dados: bytes) -> list[str]:
    try:
        programa = decodificar(dados)
    except ValueError as e:
        return [f"Binario invalido: {e}"]
    return validar_instrucoes(programa)


def exigir_ir_valido(programa: ProgramaIR) -> None:
    erros = validar_ir(programa)
    if erros:
        raise ValueError("IR invalida:\n  - " + "\n  - ".join(erros))
