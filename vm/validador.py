"""
Validacao de bytecode e instrucoes decodificadas.

Pertence a VM porque valida o formato binario que a maquina executa,
nao a representacao intermediaria do compilador.
"""
from .isa import Instrucao, NOMES_OP, decodificar


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
