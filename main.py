"""
main.py — CLI do Rover Compilador.

Uso:
  python main.py compilar programa.rover [-o saida.rvc]
  python main.py executar programa.rover
  python main.py executar programa.rvc --rvc
"""
import argparse
import sys
from pathlib import Path

from compiler import compilar, para_binario, salvar_rvc
from compiler.emissor import formatar_hex
from vm import executar_arquivo_rvc, executar_binario
from vm.estado import Mapa
from vm.maquina import ErroVM


def ler_rover(caminho: Path) -> str:
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {caminho}")
    return caminho.read_text(encoding="utf-8")


def cmd_compilar(arquivo: Path, saida: Path | None) -> int:
    codigo = ler_rover(arquivo)
    programa = compilar(codigo)

    print("IR (pc = indice da instrucao):")
    for i, instr in enumerate(programa.instrucoes):
        print(f"  {i:03d} | {instr}")
    if programa.rotulos:
        print("Rotulos:")
        for nome, idx in programa.rotulos.items():
            print(f"  {nome} -> {idx}")

    destino = saida or arquivo.with_suffix(".rvc")
    binario = salvar_rvc(programa, str(destino))
    print(f"\nBinario: {len(binario)} bytes -> {destino}")
    print(formatar_hex(binario))
    return 0


def cmd_executar(arquivo: Path, usar_rvc: bool) -> int:
    mapa = Mapa()

    if usar_rvc:
        vm = executar_arquivo_rvc(arquivo, mapa)
    else:
        codigo = ler_rover(arquivo)
        programa = compilar(codigo)
        binario = para_binario(programa)
        print(f"Compilado: {len(programa.instrucoes)} instrucoes, {len(binario)} bytes")
        print("\nExecucao VM (fetch -> decode -> execute):")
        vm = executar_binario(binario, mapa)

    print(f"\n{vm.resumo()}")
    if vm.parado and vm.mensagem:
        print(f"Alerta: {vm.mensagem}")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compilador e VM da linguagem Rover (Curiosity-L)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Ativa logs detalhados (DEBUG)"
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p_comp = sub.add_parser("compilar", help="Compila .rover para IR e .rvc")
    p_comp.add_argument("arquivo", type=Path)
    p_comp.add_argument("-o", "--saida", type=Path, default=None)

    p_exec = sub.add_parser("executar", help="Compila .rover e executa na VM")
    p_exec.add_argument("arquivo", type=Path)
    p_exec.add_argument(
        "--rvc",
        action="store_true",
        help="Arquivo ja e .rvc (nao recompila)",
    )

    args = parser.parse_args(argv)

    import logging
    nivel = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=nivel, format="%(levelname)s: %(message)s")

    try:
        if args.comando == "compilar":
            return cmd_compilar(args.arquivo, args.saida)
        if args.comando == "executar":
            return cmd_executar(args.arquivo, args.rvc)
    except (FileNotFoundError, ValueError, ErroVM) as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
