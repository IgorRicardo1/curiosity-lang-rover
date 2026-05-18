class BytecodeGenerator:
    def __init__(self):
        self.instrucoes = []
        self.contador_rotulos = 0
        self.contador_regs = 0

    def gerar(self, ast):
        self.instrucoes = []
        self.contador_rotulos = 0
        self.contador_regs = 0
        self.visitar(ast)
        return self.instrucoes

    def novo_rotulo(self):
        self.contador_rotulos += 1
        return f"ROT{self.contador_rotulos}"
        
    def novo_reg(self):
        self.contador_regs += 1
        return f"REG{self.contador_regs}"

    def visitar(self, nodo):
        if hasattr(nodo, 'data'):
            nome_metodo = f"visita_{nodo.data}"
            visitante = getattr(self, nome_metodo, self.visita_generica)
            visitante(nodo)

    def visita_generica(self, nodo):
        if hasattr(nodo, 'children'):
            for filho in nodo.children:
                self.visitar(filho)

    def obter_numero(self, nodo):
        for c in nodo.children:
            if hasattr(c, 'type') and c.type == 'NUMBER':
                return c.value
        return "0"

    def visita_avanca(self, nodo):
        self.instrucoes.append(f"EMPILHA {self.obter_numero(nodo)}")
        self.instrucoes.append("AVANCA")

    def visita_recua(self, nodo):
        self.instrucoes.append(f"EMPILHA {self.obter_numero(nodo)}")
        self.instrucoes.append("RECUA")

    def visita_gira(self, nodo):
        for c in nodo.children:
            if hasattr(c, 'value'):
                val = str(c.value).upper()
                if val in ('DIREITA', 'DIR'):
                    self.instrucoes.append("GIRA_DIREITA")
                    return
                elif val in ('ESQUERDA', 'ESQ'):
                    self.instrucoes.append("GIRA_ESQUERDA")
                    return

    def visita_se_obstaculo(self, nodo):
        rotulo_fim = self.novo_rotulo()
        self.instrucoes.append(f"PULA_SEM_OBS {rotulo_fim}")
        
        self.visita_generica(nodo)
        
        self.instrucoes.append(f"ROTULO {rotulo_fim}")

    def visita_repita(self, nodo):
        rotulo_inicio = self.novo_rotulo()
        registrador = self.novo_reg()
        
        self.instrucoes.append(f"EMPILHA {self.obter_numero(nodo)}")
        self.instrucoes.append(f"SALVA_REG {registrador}")
        self.instrucoes.append(f"ROTULO {rotulo_inicio}")
        
        self.visita_generica(nodo)
        
        self.instrucoes.append(f"DEC_PULA_NZ {registrador}, {rotulo_inicio}")