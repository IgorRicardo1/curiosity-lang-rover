"""
VM — leitor binario, validacao e ciclo fetch-decode-execute.
"""
from .carregar import carregar_arquivo, carregar_bytes
from .estado import Mapa, Rover
from .isa import Instrucao, decodificar
from .maquina import ErroVM, MaquinaVirtual
from .validador import (
    validar_binario,
    validar_instrucoes,
)


def executar_ir(programa_ir, mapa: Mapa | None = None) -> MaquinaVirtual:
    from compiler.emissor import emitir
    from compiler.validador import exigir_ir_valido

    exigir_ir_valido(programa_ir)
    return executar_binario(emitir(programa_ir), mapa)


def executar_binario(dados: bytes, mapa: Mapa | None = None) -> MaquinaVirtual:
    erros = validar_binario(dados)
    if erros:
        raise ValueError("Binario invalido:\n  - " + "\n  - ".join(erros))
    programa = carregar_bytes(dados)
    vm = MaquinaVirtual(programa, mapa)
    try:
        vm.executar()
    except ErroVM as e:
        vm.parado = True
        vm.mensagem = str(e)
    return vm


def executar_arquivo_rvc(caminho: str, mapa: Mapa | None = None) -> MaquinaVirtual:
    programa = carregar_arquivo(caminho)
    erros = validar_instrucoes(programa)
    if erros:
        raise ValueError("Programa invalido:\n  - " + "\n  - ".join(erros))
    vm = MaquinaVirtual(programa, mapa)
    try:
        vm.executar()
    except ErroVM as e:
        vm.parado = True
        vm.mensagem = str(e)
    return vm
