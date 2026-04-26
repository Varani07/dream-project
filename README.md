# Dream Project (Nome Provisório)

## Visão Geral
Este é um RPG situado em um mundo mágico, focado em criar um **ecossistema vivo e respirável** através do terminal. Diferente dos jogos convencionais onde o mundo gira em torno do jogador, aqui tanto o personagem principal quanto os NPCs têm suas próprias rotinas, objetivos, e participam ativamente do mundo — experimentando tragédias, conquistas e romances.

O projeto é desenvolvido inteiramente em **Python** utilizando a biblioteca `textual` para gerar uma interface de usuário baseada em terminal (TUI) rica e interativa.

## Principais Mecânicas

### 1. Mundo Orgânico e Estrutura Geográfica
O mundo é divido em **Mundo -> Região -> Locais**. Na interface, cada Local em uma Região é representado como uma "célula" que o jogador pode explorar.
Os NPCs não existem apenas para servir ao jogador. Eles vivem e transitam por essas células, possuindo empregos, casas, relacionamentos e ciclos de dia/noite. 

### 2. Tempo, Energia e Interrupções
O tempo no jogo é fluido e baseado em ações. Ao escolher realizar uma ação (como trabalhar, viajar entre locais ou forjar um item), a ação demandará tempo e **energia** do personagem. 
O mundo continuará rodando e simulando as rotinas dos NPCs automaticamente até que a sua ação termine, **ou** até que um evento dinâmico o interrompa (ex: um NPC o ataca ou puxa assunto).

### 3. A Troca de Protagonista
O jogador não está preso a um único "Herói". É possível alternar o controle e assumir a vida de outro personagem do mundo. Quando essa troca acontece, o antigo protagonista volta a ser um NPC e assume uma rotina própria, tomando decisões baseadas no que vivenciou no passado.

### 4. Interações e Diálogos Dinâmicos (Integração Cautelosa com LLM)
As conversas no jogo se baseiam em um sistema de **memórias**. NPCs se lembram de você, do que fez, de suas alianças e de acontecimentos do mundo. 
Para gerar conversas ricas e coerentes tanto entre Jogador e NPC quanto entre NPC e NPC, o jogo estuda o uso de modelos de Inteligência Artificial locais (LLM). O uso da IA é feito com extrema cautela e de forma seletiva (guardando em cache ou gerando diálogos em background) para não destruir a performance do jogo, e dependendo fortemente das tags de memória do sistema.
