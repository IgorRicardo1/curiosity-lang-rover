# 🚀 Rover Compilador - Curiosity-L

**Repositório:** [github.com/IgorRicardo1/curiosity-lang-rover](https://github.com/IgorRicardo1/curiosity-lang-rover)

Este projeto é um simulador de um Rover (robô explorador) em Marte. Ele inclui uma linguagem de programação própria, um tradutor (compilador) e um ambiente visual para ver o robô se movendo.

---

## 📖 1. O que é este projeto?

Imagine que você quer dar ordens a um robô em Marte. O robô não entende português diretamente, ele entende apenas números complexos.

Este projeto faz a "ponte":
1. Você escreve ordens simples em português (ex: `AVANCA(3)`).
2. Nosso **Compilador** traduz isso para uma linguagem que o robô entende.
3. Nossa **Máquina Virtual** executa essas ordens.
4. Você vê o resultado em uma tela colorida (o **Simulador**).

### 🔍 Pequeno Glossário
*   **Código-fonte (.rover):** É o seu arquivo de texto com as ordens para o robô.
*   **Compilador:** O "tradutor" que transforma seu texto em um arquivo que o robô entende.
*   **Bytecode (.rvc):** O arquivo final traduzido (binário).
*   **Simulador:** A janela que abre e mostra o robô se movendo no mapa.

---

## 🕹️ 2. Comandos da Linguagem

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

## 🛠️ 3. Guia de Início Rápido (Setup)

Você precisará do Python 3.12 ou superior instalado.
1. Instale as bibliotecas necessárias:
   ```bash
   pip install pygame lark
   ```
2. Execute o projeto:
   ```bash
   python main.py
   ```

---

## 🤓 4. Especificações Técnicas (Para Desenvolvedores)

Esta seção contém os detalhes rigorosos para quem está programando o sistema.

### Fluxo de Trabalho (Pipeline) e Status Atual
- [x] **Front-end do Compilador (Lexer/Parser):** Traduz `Arquivo .rover` ➔ `AST` (Concluído)
- [x] **Back-end do Compilador (Codegen):** Traduz `AST` ➔ `Bytecode .rvc` (Concluído)
- [ ] **Máquina Virtual (Interpretador):** Executa `Bytecode .rvc` (Pendente)
- [ ] **Simulador (Pygame):** Interface visual (Pendente)

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

### Tabela de Opcodes e Mnemônicos (ISA)
Nosso compilador gera instruções para uma **Máquina de Pilha**. Isso permite demonstrar de forma avançada como laços e condicionais são traduzidos em desvios e registradores.

| Mnemônico | Descrição |
| :--- | :--- |
| `EMPILHA n` | Coloca o valor numérico `n` no topo da pilha. |
| `AVANCA` | Consome o valor do topo da pilha e move o robô para frente. |
| `RECUA` | Consome o valor do topo da pilha e move o robô para trás. |
| `GIRA_ESQUERDA` | Vira o robô 90° à esquerda. |
| `GIRA_DIREITA` | Vira o robô 90° à direita. |
| `PULA_SEM_OBS rotulo` | Pula a execução para um `ROTULO` se o caminho à frente estiver livre. (Usado no SE OBSTACULO). |
| `SALVA_REG reg` | Salva o valor do topo da pilha em um registrador (ex: `REG1`). Usado para inicializar o loop `REPITA`. |
| `DEC_PULA_NZ reg, rotulo`| Decrementa o valor do registrador. Se o resultado NÃO for zero, pula de volta para o `ROTULO`. |
| `ROTULO nome` | Marca um endereço/destino para pulos no código. |

---

## 🗺️ 5. Ambiente e Grid
- **Mapa:** Matriz de **15 x 15** unidades.
- **Coordenadas:** De `(0,0)` até `(14,14)`.
- **Obstáculos:** Se o Rover tentar entrar em uma célula com obstáculo, a execução para e um alerta é exibido.

---

## 👥 6. Organização e Contribuição

### Estrutura de Pastas
*   `/compiler`: Lógica de tradução (Lark e Bytecode).
*   `/vm`: Motor que executa o arquivo `.rvc`.
*   `/simulator`: Parte visual (Pygame e Grid).
*   `/examples`: Pasta para os scripts que serão criados.
*   `/docs`: Documentos técnicos e PDF da Atividade A3.

### Regras de Ouro
1. **Branches:** Nunca mude a `main` direto. Use `feature/nome-da-task`.
2. **Código:** Use `snake_case` (ex: `minha_variavel`).
3. **Prazos:** Entrega final obrigatória em **08 de Junho**.
