"""
Validacao de IR — garante que a representacao intermediaria esta correta
antes da emissao de bytecode.

Pertence ao compilador porque a IR e um conceito interno do front-end/middle-end.
"""
from .ir import ProgramaIR

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


def exigir_ir_valido(programa: ProgramaIR) -> None:
    erros = validar_ir(programa)
    if erros:
        raise ValueError("IR invalida:\n  - " + "\n  - ".join(erros))
