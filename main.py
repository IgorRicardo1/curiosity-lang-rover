"""
main.py — CLI do Rover Compilador.

Uso:
  python main.py compilar programa.rover [-o saida.rvc]
  python main.py executar programa.rover [--no-visual]
  python main.py executar programa.rvc --rvc [--no-visual]
"""
import argparse
import sys
from pathlib import Path

from compiler import compilar, para_binario, salvar_rvc
from compiler.emissor import formatar_hex
from vm import executar_arquivo_rvc, executar_binario, validar_instrucoes
from vm.carregar import carregar_arquivo, carregar_bytes
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


def cmd_executar(arquivo: Path, usar_rvc: bool, no_visual: bool) -> int:
    mapa = Mapa()
    programa = []

    if usar_rvc:
        programa = carregar_arquivo(arquivo)
        erros = validar_instrucoes(programa)
        if erros:
            raise ValueError("Programa invalido:\n  - " + "\n  - ".join(erros))
    else:
        codigo = ler_rover(arquivo)
        programa_ir = compilar(codigo)
        binario = para_binario(programa_ir)
        programa = carregar_bytes(binario)
        print(f"Compilado: {len(programa_ir.instrucoes)} instrucoes, {len(binario)} bytes")

    if no_visual:
        print("\nExecucao VM (fetch -> decode -> execute):")
        if usar_rvc:
            vm = executar_arquivo_rvc(arquivo, mapa)
        else:
            vm = executar_binario(binario, mapa)
    else:
        try:
            from simulator import executar_simulacao_visual
        except ModuleNotFoundError as e:
            if e.name == "pygame":
                raise ValueError(
                    "Pygame nao instalado. Instale dependencias ou execute com --no-visual."
                ) from e
            raise
        print("\nAbrindo simulador visual...")
        vm = executar_simulacao_visual(programa, mapa, titulo=f"Curiosity-L - {arquivo.name}")

    print(f"\n{vm.resumo()}")
    if vm.parado and vm.mensagem:
        print(f"Alerta: {vm.mensagem}")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compilador e VM da linguagem Rover (Curiosity-L)"
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
    p_exec.add_argument(
        "--no-visual",
        action="store_true",
        help="Executa sem abrir janela Pygame",
    )

    args = parser.parse_args(argv)

    try:
        if args.comando == "compilar":
            return cmd_compilar(args.arquivo, args.saida)
        if args.comando == "executar":
            return cmd_executar(args.arquivo, args.rvc, args.no_visual)
    except (FileNotFoundError, ValueError, ErroVM) as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
