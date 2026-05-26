# Rover Compilador - Curiosity-L

**Repositório:** [github.com/IgorRicardo1/curiosity-lang-rover](https://github.com/IgorRicardo1/curiosity-lang-rover)

Este projeto é um simulador de um Rover (robô explorador) em Marte. Ele inclui uma linguagem de programação própria, um tradutor (compilador) e um ambiente visual para ver o robô se movendo.

---

## 1. O que é este projeto?

Imagine que você quer dar ordens a um robô em Marte. O robô não entende português diretamente — ele executa **instruções de baixo nível** (IR e binário `.rvc`).

Este projeto faz a "ponte":
1. Você escreve ordens simples em português (ex: `AVANCA(3)`).
2. Nosso **Compilador** traduz isso para uma linguagem que o robô entende.
3. Nossa **Máquina Virtual** executa essas ordens.
4. Você vê o resultado em uma tela colorida (o **Simulador**).

### Pequeno Glossário
*   **Código-fonte (.rover):** É o seu arquivo de texto com as ordens para o robô.
*   **Tokens:** Pedacinhos do código reconhecidos pelo lexer (palavras-chave, números, símbolos).
*   **AST:** Árvore de Sintaxe Abstrata — estrutura que o parser monta a partir dos tokens.
*   **Compilador:** O "tradutor" que transforma seu texto em instruções que o robô entende.
*   **Bytecode (.rvc):** O resultado final da compilação (instruções de baixo nível).
*   **Simulador:** A janela que abre e mostra o robô se movendo no mapa.

---

## 2. Comandos da Linguagem

Você pode usar os seguintes comandos para controlar o Rover (as abreviações em parênteses também são válidas!):

| Comando | O que ele faz? | Exemplo |
| :--- | :--- | :--- |
| `AVANCA(n)` ou `AVA(n)` | Move o robô para frente `n` casas. | `AVA(3)` |
| `RECUA(n)` ou `REC(n)` | Move o robô para trás `n` casas. | `REC(2)` |
| `GIRA(DIREITA)` ou `GIR(DIR)` | Vira o robô 90° para a direita. | `GIR(DIR)` |
| `GIRA(ESQUERDA)` ou `GIR(ESQ)`| Vira o robô 90° para a esquerda. | `GIRA(ESQ)` |
| `REPITA n { ... }` ou `REP n` | Repete os comandos dentro das chaves `n` vezes. | `REP 4 { AVA(1) }` |
| `SE OBSTACULO ENTAO { ... }` ou `SE OBS ENTAO { ... }`| Executa o bloco se houver um obstáculo à frente. | `SE OBS ENTAO { REC(1) }` |


---

## 3. Guia de Início Rápido (Setup)

Você precisará do Python 3.12 ou superior instalado.
1. Instale as bibliotecas necessárias:
   ```bash
   pip install -r requirements.txt
   ```
2. Para testar se o compilador ta vivo (roda todos os testes de uma vez):
   ```bash
   python -m compiler.test_compiler
   ```
   *Nota: roda sempre com o `-m` a partir da raiz do projeto, senao o Python da erro de import relativo!*

3. Para compilar um arquivo de texto para o nosso binário alienígena `.rvc`:
   ```bash
   python main.py compilar examples/exemplo.rover
   ```

4. Para ver o Rover rodando de verdade (executa o arquivo na Máquina Virtual):
   ```bash
   python main.py executar examples/exemplo.rover
   ```
   Interface visual inclui tema marciano, trilha animada do rover, partículas de poeira, camera shake em colisões, HUD de missão e alertas dinâmicos com áudio ambiente/SFX.
   Controles da janela:
   - `SPACE`: pausa/retoma animação
   - `R`: reinicia o replay da missão
   - `M`: ativa/desativa áudio
   - `ESC`: fecha o simulador
   O modo visual com Pygame abre por padrão. Para executar sem janela (modo texto/headless):
   ```bash
   python main.py executar examples/exemplo.rover --no-visual
   ```
   Se você quiser rodar direto o arquivo binário gerado (pula o compilador), usa a flag `--rvc`:
   ```bash
   python main.py executar examples/exemplo.rvc --rvc
   ```
   Também funciona em modo headless:
   ```bash
   python main.py executar examples/exemplo.rvc --rvc --no-visual
   ```

---

## 4. Especificações Técnicas

Detalhes técnicos da implementação do compilador e da máquina virtual.

### Fluxo de Trabalho (Pipeline) e Status Atual
- [x] **Análise Léxica (Lexer):** Traduz texto `.rover` ➔ **tokens** (Concluído)
- [x] **Análise Sintática (Parser):** Traduz tokens ➔ **AST** (Concluído)
- [x] **Back-end do Compilador (Codegen):** Traduz AST ➔ **IR** (mnemônicos) (Concluído)
- [x] **Emissor binário:** Traduz IR ➔ **`.rvc`** (bytes) (Concluído)
- [x] **Validação:** IR e binário (`vm/validador.py`)
- [x] **Leitor binário:** `vm/carregar.py` + `vm/isa.decodificar`
- [x] **Máquina Virtual:** fetch-decode-execute (`vm/maquina.py`)
- [x] **Simulador (Pygame):** Grid 15x15, animação do rover e alertas visuais

O pipeline completo do compilador segue o fluxo clássico:

```
Código-fonte (.rover) → [Lexer] → Tokens → [Parser] → AST → [Codegen] → IR → [Emissor] → .rvc
```

Cada fase é independente e perfeitamente isolada. O parser **não relê o texto-fonte** — ele consome os tokens injetados pelo lexer através da classe ponte `TokenStreamLexer`. Essa abordagem rigorosa impede a duplicação de processos, injetando os tokens gerados diretamente no Earley Parser do Lark.

### Arquitetura do Compilador (`/compiler`)

| Arquivo | Responsabilidade |
| :--- | :--- |
| `grammar.lark` | Gramática da linguagem (tokens em MAIÚSCULAS, regras em minúsculas) |
| `lexer.py` | Análise léxica: `tokenizacao(codigo)` → tokens |
| `parser.py` | Análise sintática: `parse_tokens(tokens)` → AST |
| `gerador_ir.py` | Geração de IR a partir da AST (`GeradorIR`) |
| `ir.py` | Estrutura `ProgramaIR` (instruções + tabela de rótulos) |
| `emissor.py` | Emissão IR → bytes `.rvc` |
| `test_compiler.py` | Script de teste das fases do compilador |
| `__init__.py` | `compilar()` e `para_binario()` |

**Erros separados por fase:**
- **Erro léxico** — palavra ou símbolo desconhecido (ex: `MOVER(5)`).
- **Erro sintático** — tokens válidos, mas ordem/estrutura inválida (ex: `AVANCA()` sem número).

### Definição da Gramática (EBNF)
A gramática atual suporta os comandos principais e suas abreviações:
```ebnf
?start: instrucao+

instrucao: movimento | direcao | controle

movimento: AVANCA "(" NUMBER ")"  -> avanca
         | RECUA "(" NUMBER ")"   -> recua

direcao: GIRA "(" SENTIDO ")"     -> gira

SENTIDO: DIREITA | ESQUERDA

controle: SE OBSTACULO ENTAO "{" instrucao+ "}" -> se_obstaculo
        | REPITA NUMBER "{" instrucao+ "}"      -> repita

AVANCA: "AVANCA" | "AVA"
RECUA: "RECUA" | "REC"
GIRA: "GIRA" | "GIR"
DIREITA: "DIREITA" | "DIR"
ESQUERDA: "ESQUERDA" | "ESQ"
REPITA: "REPITA" | "REP"
SE: "SE"
OBSTACULO: "OBSTACULO" | "OBS"
ENTAO: "ENTAO"

%import common.NUMBER
%import common.WS
%ignore WS
```

### IR e binário (.rvc)

O compilador tem **duas saídas**:

1. **IR** (`ProgramaIR`) — mnemônicos legíveis + tabela de rótulos (debug e apresentação).
2. **Binário** (`.rvc`) — sequência de bytes que a VM decodifica em instruções (`emissor.py`).

**Importante — saltos por índice de instrução:**  
Valores em `PULA_SEM_OBS` e `DEC_PULA_NZ` referem-se ao **número da instrução** na lista IR (0, 1, 2…), **não** ao offset em bytes no arquivo `.rvc`. A VM deve carregar o binário numa lista `instrucoes[]` e usar `pc` como índice nessa lista.

**Arquivo `.rvc`:** apenas o corpo binário (sem cabeçalho), para simplificar a VM.

**Codificação (1 byte = opcode):**

| Opcode | Mnemônico IR | Operandos (bytes) |
| :---: | :--- | :--- |
| `0x01` | `EMPILHA n` | `n` (1 byte, 0–255) |
| `0x02` | `AVANCA` | — |
| `0x03` | `RECUA` | — |
| `0x04` | `GIRA_ESQUERDA` | — |
| `0x05` | `GIRA_DIREITA` | — |
| `0x06` | `PULA_SEM_OBS idx` | índice da instrução (2 bytes, little-endian) |
| `0x07` | `SALVA_REG reg` | número do reg (1 byte) |
| `0x08` | `DEC_PULA_NZ reg, idx` | reg (1 byte) + índice da instrução (2 bytes) |

Rótulos **não** entram no binário — só índices já resolvidos nos saltos.

**Exemplo:** `AVA(3)` → IR `EMPILHA 3`, `AVANCA` → binário `01 03 02`.

### Tabela de Mnemônicos (ISA — IR)

| Mnemônico | Descrição |
| :--- | :--- |
| `EMPILHA n` | Coloca o valor numérico `n` no topo da pilha. |
| `AVANCA` | Consome o valor do topo da pilha e move o robô para frente. |
| `RECUA` | Consome o valor do topo da pilha e move o robô para trás. |
| `GIRA_ESQUERDA` | Vira o robô 90° à esquerda. |
| `GIRA_DIREITA` | Vira o robô 90° à direita. |
| `PULA_SEM_OBS end` | Pula para o índice `end` se o caminho à frente estiver livre (SE OBSTACULO). |
| `SALVA_REG reg` | Salva o topo da pilha no registrador (loop REPITA). |
| `DEC_PULA_NZ reg, end` | Decrementa o reg.; se ≠ 0, pula para `end`. |

---

## 5. Ambiente e Grid
- **Mapa:** Matriz de **15 x 15** unidades.
- **Coordenadas:** De `(0,0)` até `(14,14)`.
- **Obstáculos:** Se o Rover tentar entrar em uma célula com obstáculo, a execução para e um alerta é exibido.

---

## 6. Organização e Contribuição

### Estrutura de Pastas
*   `/compiler`: Lógica de tradução — lexer, parser, codegen (Lark + bytecode).
    *   `grammar.lark` — definição da gramática
    *   `lexer.py` / `parser.py` — fases léxica e sintática (cada um com sua instância Lark)
    *   `gerador_ir.py` — geração de IR
    *   `test_compiler.py` — testes do pipeline
*   `/vm`: Leitor binário, validação, VM (`isa`, `carregar`, `validador`, `maquina`, `estado`).
*   `/simulator`: Parte visual (Pygame, Grid, animação e alertas).
*   `/examples`: Pasta para scripts `.rover` de exemplo (a criar).
*   `/docs`: Documentos técnicos e PDF da Atividade A3 (a criar).
*   `main.py`: CLI (`compilar`, `executar` — VM em breve).
*   `examples/`: Scripts `.rover` de exemplo.

### Regras de Ouro
1. **Branches:** Nunca mude a `main` direto. Use `feature/nome-da-task`.
2. **Código:** Use `snake_case` (ex: `minha_variavel`).
3. **Prazos:** Entrega final obrigatória em **08 de Junho**.
