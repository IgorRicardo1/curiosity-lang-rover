"""
Emissor — traduz ProgramaIR (texto) para bytes .rvc (sem cabecalho).
"""
from .ir import ProgramaIR
from vm.isa import codificar_linha_ir


def emitir(programa: ProgramaIR) -> bytes:
    corpo = bytearray()
    for linha in programa.instrucoes:
        corpo.extend(codificar_linha_ir(linha))
    return bytes(corpo)


def salvar_rvc(programa: ProgramaIR, caminho: str) -> bytes:
    dados = emitir(programa)
    with open(caminho, "wb") as f:
        f.write(dados)
    return dados


def formatar_hex(dados: bytes, bytes_por_linha: int = 16) -> str:
    linhas = []
    for i in range(0, len(dados), bytes_por_linha):
        pedaco = dados[i : i + bytes_por_linha]
        hexs = " ".join(f"{b:02X}" for b in pedaco)
        linhas.append(f"  {i:04X}  {hexs}")
    return "\n".join(linhas)
