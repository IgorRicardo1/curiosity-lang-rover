import os
import sys


def gerar_stress(
    caminho_saida: str, nivel_aninhamento: int = 10, loops_internos: int = 250
):
    """
    Gera um programa .rover pesado.
    Cria aninhamentos de REPITA para estressar parser e gerador.
    """
    linhas = []

    for i in range(nivel_aninhamento):
        linhas.append("  " * i + f"REPITA {loops_internos} {{")

    indent = "  " * nivel_aninhamento
    linhas.append(indent + "SE OBSTACULO ENTAO {")
    linhas.append(indent + "  GIRA(ESQUERDA)")
    linhas.append(indent + "  AVANCA(1)")
    linhas.append(indent + "}")
    linhas.append(indent + "AVANCA(1)")
    linhas.append(indent + "RECUA(1)")

    for i in range(nivel_aninhamento - 1, -1, -1):
        linhas.append("  " * i + "}")
    linhas.append("AVANCA(1)\n" * 5000)

    codigo = "\n".join(linhas)
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(codigo)

    tamanho_kb = len(codigo) / 1024
    print(f"Gerado: {caminho_saida}")
    print(f"Tamanho do arquivo gerado: {tamanho_kb:.2f} KB")


if __name__ == "__main__":
    pasta_saida = os.path.dirname(__file__)
    arquivo_saida = os.path.join(pasta_saida, "stress_test.rover")

    nivel = 5
    internos = 250
    if len(sys.argv) > 1:
        nivel = int(sys.argv[1])
    if len(sys.argv) > 2:
        internos = int(sys.argv[2])

    gerar_stress(arquivo_saida, nivel, internos)
    print(
        "Para testar rode: python main.py executar examples/stress_test.rover --verbose"
    )
