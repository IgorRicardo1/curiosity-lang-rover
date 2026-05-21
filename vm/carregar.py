"""Leitor binario — arquivo .rvc ou bytes -> lista de Instrucao."""
from pathlib import Path
from .isa import Instrucao, decodificar


def carregar_bytes(dados: bytes) -> list[Instrucao]:
    return decodificar(dados)


def carregar_arquivo(caminho: str | Path) -> list[Instrucao]:
    dados = Path(caminho).read_bytes()
    return carregar_bytes(dados)
