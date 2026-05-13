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

Você pode usar os seguintes comandos para controlar o Rover:

| Comando | O que ele faz? | Exemplo |
| :--- | :--- | :--- |
| `AVANCA(n)` | Move o robô para frente `n` casas. | `AVANCA(3)` |
| `RECUA(n)` | Move o robô para trás `n` casas. | `RECUA(2)` |
| `GIRA(DIREITA)` | Vira o robô 90° para a direita. | `GIRA(DIREITA)` |
| `GIRA(ESQUERDA)` | Vira o robô 90° para a esquerda. | `GIRA(ESQUERDA)` |
| `REPITA n { ... }` | Repete os comandos dentro das chaves `n` vezes. | `REPITA 4 { ... }` |
| `SE OBSTACULO ENTAO { ... }` | Executa o bloco se houver um obstáculo à frente. | `SE OBSTACULO ENTAO { AVANCA(1) }` |

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
- [ ] **Back-end do Compilador (Codegen):** Traduz `AST` ➔ `Bytecode .rvc` (Pendente)
- [ ] **Máquina Virtual (Interpretador):** Executa `Bytecode .rvc` (Pendente)
- [ ] **Simulador (Pygame):** Interface visual (Pendente)

### Definição da Gramática (EBNF)
```ebnf
?start: instrucao+

instrucao: movimento | direcao | controle

movimento: "AVANCA(" NUMBER ")" | "RECUA(" NUMBER ")"
direcao: "GIRA(ESQUERDA)" | "GIRA(DIREITA)"
controle: "SE OBSTACULO ENTAO {" instrucao+ "}"
        | "REPITA " NUMBER " {" instrucao+ "}"

%import common.NUMBER
%import common.WS
%ignore WS
```

### Tabela de Opcodes (ISA)
| Opcode | Mnemônico | Descrição | Argumentos |
| :--- | :--- | :--- | :--- |
| `0x01` | AVANCA | Mover para frente | `n` (UInt16) |
| `0x02` | RECUA | Mover para trás | `n` (UInt16) |
| `0x03` | GIRA_ESQ | Girar 90° à esquerda | Nenhum |
| `0x04` | GIRA_DIR | Girar 90° à direita | Nenhum |
| `0x05` | DETECTA | Pulo condicional se o caminho estiver LIVRE | Endereço (UInt16) |
| `0x00` | HALT | Encerrar execução | Nenhum |

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
