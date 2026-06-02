"""
Emissor — traduz ProgramaIR (texto) para bytes .rvc (sem cabecalho).
"""
import logging
import time
from .ir import ProgramaIR
from shared.isa import codificar_linha_ir

logger = logging.getLogger(__name__)

def emitir(programa: ProgramaIR) -> bytes:
    inicio = time.time()
    corpo = bytearray()
    for linha in programa.instrucoes:
        corpo.extend(codificar_linha_ir(linha))
    resultado = bytes(corpo)
    tempo = time.time() - inicio
    logger.debug(f"[EMISSOR] Gerados {len(resultado)} bytes em {tempo:.4f}s")
    return resultado


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
