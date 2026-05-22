"""
Maquina Virtual — ciclo fetch, decode, execute.

pc = indice na lista de instrucoes (mesma numeracao da IR).
"""
from .estado import NOMES_DIRECAO, Rover, Mapa, DELTAS
from .isa import (
    Instrucao,
    OP_AVANCA,
    OP_DEC_PULA_NZ,
    OP_EMPILHA,
    OP_GIRA_DIREITA,
    OP_GIRA_ESQUERDA,
    OP_PULA_SEM_OBS,
    OP_RECUA,
    OP_SALVA_REG,
)


class ErroVM(Exception):
    pass


class MaquinaVirtual:
    def __init__(self, programa: list[Instrucao], mapa: Mapa | None = None):
        self.programa = programa
        self.mapa = mapa or Mapa()
        self.rover = Rover()
        self.pilha: list[int] = []
        self.regs: dict[int, int] = {}
        self.pc = 0
        self.parado = False
        self.mensagem: str | None = None

    def executar(self) -> Rover:
        while self.pc < len(self.programa) and not self.parado:
            instr = self._fetch()
            self.pc = self._execute(instr)
        return self.rover

    def _fetch(self) -> Instrucao:
        # Pega a proxima instrucao baseada no PC
        return self.programa[self.pc]

    def _execute(self, instr: Instrucao) -> int:
        # Decodifica e executa alterando o estado
        op = instr.opcode
        args = instr.operandos

        if op == OP_EMPILHA:
            self.pilha.append(args[0])
            return self.pc + 1

        if op == OP_SALVA_REG:
            reg = args[0]
            if not self.pilha:
                raise ErroVM("SALVA_REG com pilha vazia")
            self.regs[reg] = self.pilha.pop()
            return self.pc + 1

        if op == OP_AVANCA:
            n = self._pop_pilha("AVANCA")
            self._mover(n, frente=True)
            return self.pc + 1

        if op == OP_RECUA:
            n = self._pop_pilha("RECUA")
            self._mover(n, frente=False)
            return self.pc + 1

        if op == OP_GIRA_ESQUERDA:
            self.rover.direcao = (self.rover.direcao - 1) % 4
            return self.pc + 1

        if op == OP_GIRA_DIREITA:
            self.rover.direcao = (self.rover.direcao + 1) % 4
            return self.pc + 1

        if op == OP_PULA_SEM_OBS:
            indice = args[0]
            if not self.rover.obstaculo_a_frente(self.mapa):
                return indice
            return self.pc + 1

        if op == OP_DEC_PULA_NZ:
            reg, indice = args[0], args[1]
            valor = self.regs.get(reg, 0) - 1
            self.regs[reg] = valor
            if valor > 0:
                return indice
            return self.pc + 1

        raise ErroVM(f"Opcode nao implementado: 0x{op:02X}")

    def _pop_pilha(self, nome: str) -> int:
        if not self.pilha:
            raise ErroVM(f"{nome} com pilha vazia")
        return self.pilha.pop()

    def _mover(self, passos: int, frente: bool) -> None:
        for _ in range(passos):
            dx, dy = DELTAS[self.rover.direcao]
            if not frente:
                dx, dy = -dx, -dy
            nx, ny = self.rover.x + dx, self.rover.y + dy
            if not self.mapa.dentro(nx, ny):
                self.parado = True
                self.mensagem = f"Rover saiu do mapa em ({nx}, {ny})"
                return
            if self.mapa.tem_obstaculo(nx, ny):
                self.parado = True
                self.mensagem = f"Colisao com obstaculo em ({nx}, {ny})"
                return
            self.rover.x, self.rover.y = nx, ny

    def resumo(self) -> str:
        d = NOMES_DIRECAO[self.rover.direcao]
        base = f"Posicao ({self.rover.x}, {self.rover.y}), direcao {d}"
        if self.mensagem:
            return f"{base} — {self.mensagem}"
        return base
