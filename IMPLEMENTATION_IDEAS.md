# Ideias de Implementação e Arquitetura (Foco Prático - Python/Textual)

Este documento traz diretrizes de como arquitetar e programar o jogo focado na performance no terminal usando `textual`.

## 1. Estrutura do Mundo, Região e Locais
A arquitetura do mundo do jogo segue uma hierarquia: `World` contém `Regions`, que por sua vez contêm `Locais`.
- Na UI (`textual`), quando o jogador acessa uma `Region`, a interface deve desenhar um `Grid` (malha) onde cada "célula" é um `Local` (ex: Taverna, Forja, Floresta).
- O jogador e os NPCs ocupam essas células.
- **Transição e Descoberta:** Mover-se para células não descobertas (Fog of War) gasta mais tempo e energia. O jogador só interage com o conteúdo do Local atual.

## 2. Sistema de Tempo Baseado em Ação (Time-Skip com Interrupções)
No jogo, o relógio não precisa bater segundo por segundo em tempo real. Ele avança em blocos baseados no que o jogador faz.
- **Ação:** O jogador decide "Viajar para a Capital" (Duração: 4 horas) ou "Dormir" (Duração: 8 horas).
- **O Loop de Simulação:** Ao iniciar a ação, o controlador de tempo avança o relógio em incrementos (ex: de 5 em 5 minutos). Em cada incremento, a lógica verifica a rotina dos NPCs.
- **Interrupção:** Durante o "avanço rápido", o sistema verifica gatilhos de eventos. Se no minuto 45 um NPC hostil entra no mesmo Local que o jogador, o avanço rápido é **interrompido**. O jogador recebe uma notificação na UI e precisa reagir, e a ação original falha ou é pausada.

## 3. Unificação de Entidades e Troca de Personagem
- Não crie classes separadas para `Player` e `NPC`. Crie uma classe genérica `Entity` que contenha: Atributos, Energia, Memórias, Local Atual.
- A diferença se dá pelo **Input**: A `Entity` que for o jogador obedece aos botões do `textual`. As `Entities` NPC obedecem a um agendador de tarefas/rotinas.
- **A Troca:** Mudar de personagem é apenas plugar o Input do teclado na nova Entidade, e dar à Entidade antiga uma lista de tarefas (rotina) de NPC.

## 4. Integração Cautelosa com LLM (Conversas NPC-NPC e Player-NPC)
A grande armadilha de usar IA em jogos de simulação é que o tempo para gerar a resposta trava a UI e queima CPU. 
- **Filtragem Rígida:** Não use a IA para cumprimentos simples ou falas genéricas (Use templates fixos ou gerados por código).
- **Prompt com Memórias Estruturadas:** A IA não sabe jogar o jogo. O que o LLM fará é traduzir "Fatos" em "Texto Narrativo". O jogo alimenta o LLM com as memórias: `[Relacionamento: Ruim] [Memória: Protagonista roubou a loja] [Ação: NPC recusa a vender]`. O LLM escreve a fala.
- **Processamento Assíncrono:** Quando dois NPCs começam a fofocar do outro lado do mapa, a geração desse diálogo deve ir para uma fila de background (Asyncio). A resposta só é anexada no log quando pronta, sem travar o jogo.

## 5. Simulação de Fundo (Background Simulation)
Para o jogo não explodir processando NPCs que estão em outra `Region`:
- Calcule rotinas apenas usando matemática. Se um NPC está na Cidade vizinha e o jogador viaja de carroça por 4 horas, não simule cada passo do NPC. Apenas verifique: *O NPC tinha a tarefa de ir trabalhar às 8h? Agora são 12h, então mova ele para o Local "Trabalho" e desconte sua energia*.
