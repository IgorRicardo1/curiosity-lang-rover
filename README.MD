# Rover Compilador - Curiosity-L

## 1. Stack Tecnológica e Funcionamento do Projeto

Este documento descreve as ferramentas e tecnologias selecionadas para o desenvolvimento do compilador, da máquina virtual e do simulador.

### 1.1. Linguagem de Desenvolvimento
- **Python 3.12+**: Escolhida pela alta produtividade e vasta biblioteca padrão para manipulação de strings e estruturas de dados, essencial para o cumprimento do cronograma.

### 1.2. Módulo de Compilação
- **Lark (Parsing Library)**: Utilizada para implementar a gramática EBNF da Curiosity-L. O Lark facilita a criação da Árvore de Sintaxe Abstrata (AST) de forma rápida e segura.
- **Gerador de Bytecode**: Módulo personalizado em Python que percorre a AST e traduz os nós em uma sequência de opcodes numéricos (formato binário ou .bin).

### 1.3. Execução (Back-end / VM)
- **Curiosity-VM**: Uma Máquina Virtual baseada em pilha (stack-based), desenvolvida para ler o arquivo de bytecode e gerenciar o estado do rover.
- **Gerenciador de Estado**: Componente que controla as coordenadas (x, y) e a orientação (N, S, E, W) do rover.

### 1.4. Interface e Simulação
- **Pygame**: Biblioteca para a visualização 2D do grid de Marte. Permite animações fluidas do movimento do rover e renderização de obstáculos.
- **Docker**: Utilizado para empacotar todo o ambiente de execução (compilador + simulador), garantindo portabilidade e consistência durante a apresentação.

## 2. Regras de Negócio

Este capítulo estabelece as normas de funcionamento da linguagem e as restrições do ambiente de simulação do Rover Espacial.

### 2.1. Definições da Linguagem (Curiosity-L)
- **Comandos de Movimento**: A linguagem deve suportar avançar e recuar em $n$ posições e girar 90º para ambos os lados.
- **Percepção**: O comando de detecção deve retornar um valor booleano indicando a presença de obstáculos à frente.
- **Estruturas Avançadas**: Implementação de condicionais (`IF OBSTACLE`) e laços de repetição (`REPEAT n`) para automação de trajetórias.

### 2.2. O Ambiente (Grid de Marte)
- **Dimensões**: Matriz mínima de 15 x 15 unidades de deslocamento.
- **Colisões**: O rover não pode ocupar a mesma célula de um obstáculo. Tentativas de movimento contra obstáculos devem interromper a execução e gerar um alerta.
- **Limites do Mapa**: Movimentos que levem o rover para fora das coordenadas (0,0) a (14,14) devem ser tratados como erros de tempo de execução.

### 2.3. Tratamento de Erros e Validação
- **Erro de Sintaxe**: O compilador deve identificar e informar a linha exata onde um comando foi escrito incorretamente.
- **Erro de Parâmetro**: Valores inválidos (ex: `MOVE(-5)` ou `REPEAT(0)`) devem ser bloqueados na análise semântica.
- **Validação de Bytecode**: A VM deve verificar a integridade do arquivo antes de iniciar a execução para evitar opcodes desconhecidos.

### 2.4. Ciclo de Execução
1. **Leitura**: O script de texto é carregado pelo sistema.
2. **Compilação**: O código é validado e convertido em bytecode.
3. **Simulação**: A VM executa o bytecode sequencialmente, atualizando a posição no grid a cada instrução.
4. **Feedback**: A cada passo, o estado atual (posição e direção) é exibido visualmente para o usuário.

