"""Estado do rover e mapa 15x15."""
from dataclasses import dataclass, field

TAMANHO_MAPA = 15

# 0=Norte (y-1), 1=Leste (x+1), 2=Sul (y+1), 3=Oeste (x-1)
DELTAS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
NOMES_DIRECAO = ["N", "L", "S", "O"]

@dataclass
class Mapa:
    obstaculos: set[tuple[int, int]] = field(default_factory=set)

    def dentro(self, x: int, y: int) -> bool:
        return 0 <= x < TAMANHO_MAPA and 0 <= y < TAMANHO_MAPA

    def tem_obstaculo(self, x: int, y: int) -> bool:
        return (x, y) in self.obstaculos

@dataclass
class Rover:
    x: int = 7
    y: int = 7
    direcao: int = 2

    def celula_a_frente(self) -> tuple[int, int]:
        dx, dy = DELTAS[self.direcao]
        return self.x + dx, self.y + dy

    def obstaculo_a_frente(self, mapa: Mapa) -> bool:
        fx, fy = self.celula_a_frente()
        return not mapa.dentro(fx, fy) or mapa.tem_obstaculo(fx, fy)
