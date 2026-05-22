from .ir import ProgramaIR


class GeradorIR:
    def __init__(self):
        self.instrucoes = []
        self.rotulos = {}
        self.contador_rotulos = 0
        self.contador_regs = 0

    def gerar(self, ast) -> ProgramaIR:
        self.instrucoes = []
        self.rotulos = {}
        self.contador_rotulos = 0
        self.contador_regs = 0
        self.visitar(ast)
        return ProgramaIR(
            instrucoes=self._resolver_saltos(),
            rotulos=dict(self.rotulos),
        )

    def novo_rotulo(self):
        self.contador_rotulos += 1
        return f"ROT{self.contador_rotulos}"

    def marcar_rotulo(self, nome):
        """Proxima instrucao emitida tera este indice (usado nos saltos)."""
        self.rotulos[nome] = len(self.instrucoes)

    def novo_reg(self):
        self.contador_regs += 1
        return f"REG{self.contador_regs}"

    def _resolver_saltos(self):
        """Substitui nomes de rotulos por indices de instrucao (nao bytes)."""
        resolvidas = []
        for instr in self.instrucoes:
            if instr.startswith("PULA_SEM_OBS "):
                nome = instr.split(maxsplit=1)[1]
                resolvidas.append(f"PULA_SEM_OBS {self.rotulos[nome]}")
            elif instr.startswith("DEC_PULA_NZ "):
                resto = instr[len("DEC_PULA_NZ ") :]
                reg, nome = resto.split(", ")
                resolvidas.append(f"DEC_PULA_NZ {reg}, {self.rotulos[nome]}")
            else:
                resolvidas.append(instr)
        return resolvidas

    def visitar(self, nodo):
        if hasattr(nodo, "data"):
            nome_metodo = f"visita_{nodo.data}"
            visitante = getattr(self, nome_metodo, self.visita_generica)
            visitante(nodo)

    def visita_generica(self, nodo):
        if hasattr(nodo, "children"):
            for filho in nodo.children:
                self.visitar(filho)

    def visitar_comandos_bloco(self, nodo):
        """Visita apenas nos instrucao dentro de { ... } (repita / se)."""
        for filho in nodo.children:
            if getattr(filho, "data", None) == "instrucao":
                self.visitar(filho)

    def obter_numero(self, nodo):
        for c in nodo.children:
            if hasattr(c, "type") and c.type == "NUMBER":
                val = int(c.value)
                if not 0 <= val <= 255:
                    raise ValueError(f"Numero fora do limite permitido (0-255): {val}")
                return val
        raise RuntimeError(f"AST corrompida: Numero esperado na instrucao {nodo.data.upper()}")

    def visita_avanca(self, nodo):
        numero = self.obter_numero(nodo)
        if numero <= 0:
            return
        self.instrucoes.append(f"EMPILHA {numero}")
        self.instrucoes.append("AVANCA")

    def visita_recua(self, nodo):
        numero = self.obter_numero(nodo)
        if numero <= 0:
            return
        self.instrucoes.append(f"EMPILHA {numero}")
        self.instrucoes.append("RECUA")

    def visita_gira(self, nodo):
        for c in nodo.children:
            if hasattr(c, "value"):
                val = str(c.value).upper()
                if val in ("DIREITA", "DIR"):
                    self.instrucoes.append("GIRA_DIREITA")
                    return
                elif val in ("ESQUERDA", "ESQ"):
                    self.instrucoes.append("GIRA_ESQUERDA")
                    return

    def visita_se_obstaculo(self, nodo):
        rotulo_fim = self.novo_rotulo()
        self.instrucoes.append(f"PULA_SEM_OBS {rotulo_fim}")
        self.visitar_comandos_bloco(nodo)
        self.marcar_rotulo(rotulo_fim)

    def visita_repita(self, nodo):
        numero = self.obter_numero(nodo)
        if numero <= 0:
            return
            
        rotulo_inicio = self.novo_rotulo()
        registrador = self.novo_reg()

        self.instrucoes.append(f"EMPILHA {numero}")
        self.instrucoes.append(f"SALVA_REG {registrador}")
        self.marcar_rotulo(rotulo_inicio)

        self.visitar_comandos_bloco(nodo)

        self.instrucoes.append(f"DEC_PULA_NZ {registrador}, {rotulo_inicio}")
