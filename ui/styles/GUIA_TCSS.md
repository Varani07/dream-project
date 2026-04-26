# Guia Completo de Estilização com Textual (TCSS)

O Textual utiliza uma linguagem própria de folhas de estilo muito semelhante ao CSS da web, chamada **TCSS** (.tcss). Assim como na web, a função principal do TCSS é separar a "Lógica e Estrutura" (o código em Python) do "Visual e Layout" (cores, tamanhos, posições).

## 1. Por que a altura da Barra não funcionava?
O erro que você presenciou com a barra horizontal ocorreu por dois motivos básicos de hierarquia e cálculo de caixa (_Box Model_):
1. **Estilo Inline Python vs TCSS:** No seu `app.py`, dentro do `on_mount`, havia a linha `self.barra.styles.height = 3`. Os estilos definidos diretamente via código no Python (inline) **têm prioridade máxima**. Eles "atropelam" o que estiver no arquivo `.tcss`. Para resolver, apagamos essa linha do Python para que o CSS volte a mandar.
2. **O Box Model:** Ao setarmos `height: 3` na barra, e em seguida colocarmos `border-top: solid $primary`, a borda ocupa 1 linha da altura total, sobrando apenas 2 para o botão. Botões no Textual costumam usar 3 linhas (devido à própria estilização padrão deles). Alteramos a altura no CSS para `auto`, que instrui o contêiner a crescer magicamente para o tamanho exato dos botões/textos que estiverem dentro dele.

---

## 2. Conceitos Essenciais de TCSS

### Seletores
Como referenciar os itens para pintá-class?
- **Tag do Widget**: Se você escrever `Button { color: red; }`, afetará **todos** os botões do aplicativo.
- **Classe**: Widgets podem ter classes (`Button("OK", classes="botao-perigoso")`). No CSS você chama por `.botao-perigoso { ... }`.
- **ID (#)**: O ID é único. O que fizemos com `id="mapa"`, referenciamos no CSS por `#mapa { ... }`.

### O Box Model do Terminal
No Textual, o tamanho se dá em "células do terminal" (caracteres), não em pixels.
- `width: 50;` = Ocupará a largura de 50 letras no terminal.
- `height: 3;` = Ocupará 3 linhas do terminal de altura.
- Frações: `width: 1fr;` = Ocupa tudo que restar (1 fração). Se dois itens têm `1fr`, eles racham a tela meio a meio.
- Relativo: `width: 50%;` = Metade da tela.

### Posicionamento e Layout
Contêineres como `Horizontal` e `Vertical` já organizam seus filhos em linha ou coluna automaticamente. Mas você pode mudar regras:
- `align: center middle;`: Centraliza o conteúdo horizontal e verticalmente. (Apenas se o contêiner for maior que o filho).
- `content-align: center middle;`: Onde o texto se alinha dentro do botão ou Label.
- `dock: bottom;`: Tira o elemento da organização natural da tela e prega ele na parte inferior (rodapé), não importa o que aconteça acima dele.
- `margin: 1 2;`: Margem externa (afasta dos vizinhos). Adiciona 1 linha de espaço em cima/baixo e 2 espaços na esquerda/direita.
- `padding: 1 2;`: Margem interna (engorda o widget). 

### Variáveis e Temas do Textual
Reparou que no código eu usei coisas como `$primary` ou `$accent` em vez de "#FF0000" (Vermelho) ou "blue"?
O Textual tem um excelente sistema de temas atrelado. Ao usar variáveis como `$primary`, `$secondary`, `$success`, `$panel`, o Textual vai colorir isso perfeitamente e, se você apertar a letra `d` para mudar para o Dark Mode (modo noturno), todas essas cores vão se reajustar sozinhas para as paletas oficiais noturnas.

## 3. Guia Prático para o Futuro
Se você for criar um novo menu de inventário (exemplo):
1. No `app.py`, crie as estruturas sem se preocupar em ficar bonito. Exemplo:
   ```python
   yield Vertical(
       Static("Sua Mochila", id="titulo_inventario"),
       Horizontal(
            Button("Poção", id="item_pocao"),
            Button("Espada", id="item_espada"),
            id="area_itens"
       ),
       id="container_inventario"
   )
   ```
2. Abra seu `styles/app.tcss`.
3. Use os seletores que você criou:
   ```css
   #container_inventario {
       background: $panel;      /* Coloca cor de fundo */
       border: round $primary;  /* Coloca uma borda redondinha colorida */
       width: 60%;              /* Inventário centralizado sem tapar tudo */
       height: auto;            /* Adapta altura */
   }

   #titulo_inventario {
       content-align: center middle; 
       text-style: bold;        /* Deixa negrito */
   }

   #item_pocao {
       background: red;         /* Poções são vermelhas, quebrando o tema normal */
   }
   ```
4. Recarregue e pronto!
