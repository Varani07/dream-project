# Dream Project — Migração de Python para Go

> RPG textual de mundo vivo, sendo reescrito de Python (`textual`) para Go (`bubbletea` + `lipgloss` + `bubbles`).
>
> Este README é um **guia de migração comentado para quem só conhece Python**. Cada bloco Go vem acompanhado de explicação linha-a-linha, comparação com o equivalente Python já existente no projeto, e opinião de design quando faz sentido.

---

## Sumário

1. [Por que migrar para Go?](#por-que-migrar-para-go)
2. [Diferenças mentais Python → Go](#diferenças-mentais-python--go)
3. [Estrutura nova do projeto](#estrutura-nova-do-projeto)
4. [Setup inicial: go.mod, ferramentas, layout](#setup-inicial-gomod-ferramentas-layout)
5. [Camada por camada](#camada-por-camada)
   - [5.1 ECS: Entity + Component + Registry (`ecs/`)](#51-ecs-entity--component--registry-ecs)
   - [5.2 Componentes: um arquivo por tipo (`components/`)](#52-componentes-um-arquivo-por-tipo-components)
   - [5.3 Event Bus](#53-event-bus)
   - [5.4 Mundo, Região, Localização, Cômodo](#54-mundo-região-localização-cômodo)
   - [5.5 Tempo](#55-tempo)
   - [5.6 Sistemas (vitalidade, diálogo) — auto-registro](#56-sistemas-vitalidade-diálogo--auto-registro)
   - [5.7 Diálogo: pipeline, templates, intenções](#57-diálogo-pipeline-templates-intenções)
   - [5.8 Save / Load](#58-save--load)
   - [5.9 UI com Bubble Tea](#59-ui-com-bubble-tea)
6. [Erros, em vez de exceções](#erros-em-vez-de-exceções)
7. [Concorrência: goroutines, channels e ticks de tempo](#concorrência-goroutines-channels-e-ticks-de-tempo)
8. [Roadmap sugerido (ordem de migração)](#roadmap-sugerido-ordem-de-migração)
9. [Opiniões e dicas práticas](#opiniões-e-dicas-práticas)
10. [Padrões de escalabilidade](#10-padrões-de-escalabilidade)

---

## Por que migrar para Go?

**O que você ganha:**

- **Binário único.** `go build` gera um executável estático. Sem `pip install`, sem `requirements.txt`, sem ambiente virtual. Você manda um arquivo para alguém e roda.
- **Performance previsível.** O loop de tempo do mundo, a propagação de eventos, a busca em listas de entidades — tudo isso fica ordens de magnitude mais rápido. Mais importante: sem pausas estranhas do GC do Python sob carga.
- **Concorrência de verdade.** Goroutines e channels resolvem com elegância coisas como "tick de tempo automático" e "eventos assíncronos do mundo", que em Python você está simulando com `set_interval` do Textual.
- **Tipagem estática real.** Hoje você usa `dataclass` + `TypeVar` + `cast`. O compilador Go vai te pegar erros que o `mypy` deixaria passar (ou que você nem está rodando).

**O que você perde (e como compensar):**

- **REPL/iteração rápida.** Não tem `python -c`. Mitigue com testes pequenos (`go test`) e `go run .`.
- **Flexibilidade de tipagem dinâmica.** Sem `**kwargs`, sem monkey-patching, sem `getattr` mágico. Você terá que ser mais explícito.
- **Decorators.** Não existem em Go. Vamos trocar `@event_bus.subscribe(...)` por chamadas explícitas — o que é, na minha opinião, **melhor** a longo prazo, porque o fluxo fica visível.
- **Textual.** Sem equivalente direto. Vamos usar **Bubble Tea** (Charmbracelet), que segue o padrão Elm/TEA (Model-View-Update). Mais sobre isso na [seção 5.8](#58-ui-com-bubble-tea).

---

## Diferenças mentais Python → Go

Antes de mexer em qualquer linha, internalize essas equivalências. Vou repetir várias delas com código depois, mas tê-las na cabeça facilita muito.

| Python | Go | Comentário |
| --- | --- | --- |
| `class Foo:` | `type Foo struct { ... }` | Não existe classe; existe struct (dados) e funções com receiver (comportamento). |
| `def metodo(self, x):` | `func (f *Foo) Metodo(x int)` | O `self` vira "receiver". `*Foo` = ponteiro (modifica o original). `Foo` (sem `*`) = cópia. |
| `@dataclass` | `type Foo struct{ A int; B string }` | Em Go toda struct já é literalmente "uma dataclass". Sem decorator. |
| `__init__` | Função `NewFoo(...) *Foo` (convenção) | Não há construtor especial; cria-se uma função `NewX`. |
| `raise Exception` | `return err` | Não há exceções (existe `panic`, mas é só para coisas realmente catastróficas). |
| `try/except` | `if err != nil { ... }` | Você verifica o erro logo após cada chamada que pode falhar. |
| `None` | `nil` | `nil` funciona para ponteiros, slices, maps, channels, interfaces, funções. Em outros casos use o zero-value. |
| `list[T]` | `[]T` | Slice. É o "list" do Go. |
| `dict[K, V]` | `map[K]V` | Map. Idêntico em uso. |
| `tuple[int, int]` | `[2]int` ou `struct{X, Y int}` | Go não tem tupla. Para coordenadas, prefiro struct nomeada (`Coord{X, Y int}`). |
| `Enum` | `const ( A SomeType = iota; B; C )` | Mais primitivo, mas funciona. |
| `Protocol` | `interface{ ... }` | Em Go, interface é **implícita** — se sua struct tem os métodos certos, ela já implementa, sem `class Foo(Protocol)`. |
| `mixin` | embedding (`type Foo struct { BarMixin }`) | Composição em vez de herança. |
| `@decorator` | função que recebe outra função, chamada explicitamente | Não há sintaxe. Você passa funções como valores. |
| `from x import y` | `import "modulo/pacote"` + `pacote.Y` | Imports são por **pacote** (= pasta), não por arquivo. Identificadores **maiúsculos** são exportados, **minúsculos** são privados. |
| `__init__.py` | não existe equivalente | A pasta **é** o pacote. Não há "barrel file". |
| `if __name__ == "__main__":` | `func main()` no pacote `main` | Só executa o `main()` do pacote `main`. |

Mais uma diferença vital: **não há herança de implementação**. Quando você quer "estender", você ou (a) usa embedding (compõe a struct dentro de outra), ou (b) define uma interface e implementa-a. Esquece a árvore `BaseScreen` → `MainMenu` → ... do Textual; em Go cada tela é uma struct independente que implementa a interface `tea.Model`.

---

## Estrutura nova do projeto

Em Go, o **diretório é o pacote**. Não tem `__init__.py`. Layout sugerido (baseado no projeto Python atual):

```
dream-project/
├── go.mod                          # equivalente a requirements.txt + setup.py
├── go.sum                          # lock file (gerado automaticamente)
├── main.go                         # entry point — substitui main.py (package main, func main())
├── internal/                       # código privado ao módulo (ninguém de fora importa)
│   ├── core/
│   │   ├── geom/                   # tipos compartilhados, ZERO dependências
│   │   │   └── coord.go            # Coord{X,Y} usado por mundo, components, events
│   │   ├── ecs/                    # núcleo do Entity-Component-System
│   │   │   ├── entity.go           # Entity + métodos Add/All
│   │   │   ├── component.go       # Component interface + Register/NewByName/NameOf
│   │   │   ├── get.go              # Get[T], Has[T], Require[T] (genéricos)
│   │   │   └── entity_test.go
│   │   ├── components/             # UM ARQUIVO POR COMPONENT — auto-registrado via init()
│   │   │   ├── identity.go         # Identity + PlayerControl
│   │   │   ├── vitality.go
│   │   │   ├── location.go         # Location + WorldKnowledge
│   │   │   ├── personality.go
│   │   │   └── affinity.go
│   │   ├── events/                 # um arquivo por DOMÍNIO de evento (não tudo num types.go)
│   │   │   ├── bus.go
│   │   │   ├── time.go             # TimeAdvanced
│   │   │   ├── world.go            # WorldLogMessage
│   │   │   └── dialogue.go         # SpeechEmitted, AffinityChanged
│   │   ├── world/
│   │   │   ├── world.go            # World agora carrega Bus, TimeManager, RNG (DI container)
│   │   │   ├── region.go
│   │   │   ├── location.go
│   │   │   ├── room.go
│   │   │   └── factory.go          # NewInitialWorld (era classmethod no Python)
│   │   ├── timemgr/                # nome do pacote != "time" (evita colisão com stdlib)
│   │   │   └── manager.go
│   │   ├── systems/                # cada sistema se registra via init() — addNew = um arquivo
│   │   │   ├── registry.go         # Register(fn), RunAll(w)
│   │   │   ├── vitality.go
│   │   │   └── needs.go            # exemplo futuro: fome, sono, etc.
│   │   ├── dialogue/
│   │   │   ├── intention.go
│   │   │   ├── pipeline.go
│   │   │   ├── handlers.go
│   │   │   └── templates.go        # carrega de data/dialogue/templates/*.json (ver §10)
│   │   └── factory/                # construtores de Entity de alto nível
│   │       ├── player.go           # CreatePlayer
│   │       └── npc.go              # CreateNPC
│   ├── data/
│   │   ├── save.go
│   │   └── load.go                 # usa ecs.NewByName — sem mapa hardcoded
│   ├── ui/
│   │   ├── app.go                  # tea.Model raiz
│   │   ├── screens/
│   │   │   ├── menu.go
│   │   │   ├── newgame.go
│   │   │   ├── loadgame.go
│   │   │   └── game.go
│   │   └── widgets/
│   │       ├── status.go
│   │       ├── minimap.go
│   │       ├── worldlog.go
│   │       └── analysis.go
│   └── utils/
│       ├── files.go
│       ├── timefmt.go
│       └── probability.go
└── data/                           # conteúdo do jogo + saves, tudo em JSON
    ├── saves/                      # saves dos jogadores
    ├── dialogue/templates/         # 1 arquivo por arquétipo (amigavel.json, etc.)
    ├── world/locations.json        # LOCATION_TYPES do Python vira data file
    └── world/rooms.json            # ROOM_TYPES idem
```

**Por que `internal/`?** É uma convenção Go: pacotes dentro de `internal/` só podem ser importados pelo próprio módulo. Como você não está publicando isso como biblioteca, todo o seu código vai pra lá. É o "private package" do Go.

**Por que `main.go` na raiz e não em `cmd/dream/`?** Pra projeto com **um binário só**, raiz é mais simples: `go run .` em vez de `go run ./cmd/dream`, e um nível a menos de pasta. O layout `cmd/<nome>/main.go` é uma convenção comunitária (não oficial do Go) que faz sentido quando você tem **múltiplos executáveis** (ex: `cmd/dream/`, `cmd/dream-editor/`, `cmd/dream-server/`) ou quando o pacote raiz é importável como biblioteca. Nada disso é o seu caso hoje, e migrar de raiz para `cmd/` no futuro é literalmente um `mv`. Se aparecer um segundo binário, aí vale mover.

**Por que `geom/` separado, com só `Coord{X,Y}` dentro?** Coord é usado por **mundo, componentes, eventos e UI**. Se ele morar em qualquer um desses, os outros que precisarem dele têm que importar aquele pacote — e o Go **não compila dependência cíclica entre pacotes**. A regra de ouro: tipos básicos compartilhados moram **embaixo**, num pacote sem dependências, para que qualquer um possa importar sem risco. Esse padrão se repete: se um dia surgir `Color`, `Direction`, `Range`, eles vão em `geom/` (ou num `primitives/` irmão).

**Por que `ecs/` em vez do antigo `entity/`?** Porque a pasta agora abriga *três* coisas relacionadas mas distintas: a struct `Entity`, a interface `Component`, e o **registry** de componentes (para save/load e introspection). `ecs/` (Entity-Component-System) descreve melhor o conjunto. Não muda nada técnico; é só clareza.

**Por que `components/` é um pacote separado, com um arquivo por componente?** Esta é a **mudança chave de escalabilidade**:

- **Um arquivo por componente** significa que adicionar um novo (`Hunger`, `Skills`, `Inventory`, `Combat`...) é criar **um arquivo**, sem mexer em nenhum outro. PRs ficam pequenos e isolados.
- O arquivo do componente **se auto-registra** no `ecs.Registry` via `func init()` (veja §5.1 e §5.2). Save/load funcionam sem precisar editar nenhuma lista central.
- Separar `components/` do `ecs/` evita import cíclico: `components` importa `ecs.Component`, mas `ecs` não precisa saber sobre componentes concretos.
- Cada arquivo carrega **só o que pertence ao componente** (struct, construtor, métodos, `init` de registro). Nada de "dataclass + lógica espalhada".

**Por que `events/` também é um arquivo por domínio?** Mesma lógica: hoje em Python `types.py` tem 4 eventos. Daqui a 6 meses vai ter 40. Quebrar por domínio (`time.go`, `dialogue.go`, `world.go`, `combat.go`...) evita que o arquivo vire um Frankenstein. Nada impede colocar tudo num `types.go` agora — mas o hábito de já criar separado evita refactor doloroso depois.

**Por que `systems/` com `registry.go`?** Mesmo padrão de auto-registro: cada arquivo de sistema chama `systems.Register(...)` em `init()`. O `World` pega tudo registrado e roda. Adicionar um sistema = criar um arquivo. Nunca mais "esqueci de chamar `register_systems()` pro meu sistema novo".

**Por que `factory/` separado, e não dentro de `ecs/` ou `components/`?** Porque um factory **junta** vários componentes para formar uma entidade concreta (player, NPC, monstro, item). Se o factory morasse em `components/`, o pacote teria que importar regras de negócio (que classes sociais existem, que arquétipos vêm por padrão, etc.). Manter `factory/` separado deixa `components/` puro: só estrutura de dados.

**Por que `data/` agora tem `dialogue/templates/`, `world/locations.json`, etc.?** Hoje em Python, `TEMPLATES`, `LOCATION_TYPES`, `ROOM_TYPES`, `VALID_ARCHETYPES`, `INITIAL_CITY_COMPOSITION` são todos **dicts hardcoded em código**. Isso é teto de escalabilidade: cada novo arquétipo, cada novo tipo de cômodo, exige editar e recompilar. Movendo para JSON, adicionar conteúdo vira **adicionar arquivo**. Mais sobre isso em [§10 Padrões de escalabilidade](#10-padrões-de-escalabilidade).

---

## Setup inicial: go.mod, ferramentas, layout

### Instalando Go

```bash
# Arch / Manjaro
sudo pacman -S go
# Debian / Ubuntu
sudo apt install golang-go
# ou baixe de https://go.dev/dl/
```

Confirme:

```bash
go version   # esperado: go1.22+ (qualquer >= 1.21 serve)
```

### Inicializando o módulo

Dentro de `dream-project/`:

```bash
go mod init github.com/seuuser/dream-project
```

Isso cria o `go.mod`. O nome do módulo (a URL) é só um identificador único — não precisa existir no GitHub agora. Você importa coisas como `"github.com/seuuser/dream-project/internal/core/ecs"`.

### Dependências que vamos usar

```bash
go get github.com/charmbracelet/bubbletea
go get github.com/charmbracelet/bubbles
go get github.com/charmbracelet/lipgloss
go get github.com/google/uuid
```

Explicação rápida:

- **bubbletea** — framework TUI (substitui `textual`). Modelo Elm: `Model` (estado) + `Update` (transição) + `View` (renderização).
- **bubbles** — biblioteca de widgets prontos (lista, input, viewport, etc).
- **lipgloss** — styling de strings (cores, bordas, padding). Substitui a marcação `[red]...[/]` do Textual e parte do CSS.
- **google/uuid** — equivalente de `uuid.uuid4()`.

### Comandos do dia a dia

```bash
go run .                      # roda o jogo (use o caminho do pacote main; "." = pacote do diretório atual)
go build -o dream .           # gera binário
go test ./...                 # roda todos os testes
go vet ./...                  # análise estática (sempre rode antes de commitar)
gofmt -w .                    # formata tudo (existe também: goimports)
```

### O `main.go` mínimo (esqueleto)

Para começar, esse é o equivalente direto do seu `main.py`:

```python
# main.py (Python — o que existe hoje)
from app import GameApp

if __name__ == "__main__":
    GameApp().run()
```

```go
// main.go (Go — na raiz do projeto)
package main

import (
    "fmt"
    "os"

    tea "github.com/charmbracelet/bubbletea"

    "github.com/seuuser/dream-project/internal/ui"
)

func main() {
    // tea.NewProgram cria a "engine" do Bubble Tea ao redor do nosso Model raiz.
    // ui.NewApp() devolve a tela inicial (menu) — equivalente ao GameApp() do Python.
    p := tea.NewProgram(ui.NewApp(), tea.WithAltScreen())

    // p.Run() bloqueia até o usuário sair. Equivalente ao .run() do Textual.
    // Retorna (Model_final, error). Ignoramos o model; só checamos o erro.
    if _, err := p.Run(); err != nil {
        // fmt.Fprintln escreve na stderr. Em Python: print(..., file=sys.stderr).
        fmt.Fprintln(os.Stderr, "erro fatal:", err)
        os.Exit(1)
    }
}
```

**Coisas para notar:**

- **`package main` é obrigatório.** Só esse pacote gera binário; qualquer outro nome vira biblioteca.
- **`func main()` é o ponto de entrada.** Sem parâmetros, sem retorno. Argumentos de linha de comando vêm de `os.Args` (slice de strings).
- **Não existe `if __name__ == "__main__":`.** Não é preciso — só o `main()` do pacote `main` roda como executável.
- **`tea.WithAltScreen()` é uma "option".** Padrão comum em Go: funções `WithX` que configuram o construtor. Aqui significa "usa tela alternativa do terminal" — igual ao que `vim` ou `htop` fazem.
- **Pra começar SEM Bubble Tea** (passo 1 do roadmap), você pode fazer um `main.go` ainda mais minimalista só pra confirmar que o setup tá ok:

  ```go
  package main

  import "fmt"

  func main() {
      fmt.Println("dream-project: build ok")
  }
  ```

  `go run .` deve imprimir a frase. Aí você sabe que `go.mod`, módulo e ferramentas estão certos antes de adicionar dependências.

---

## Camada por camada

A partir daqui, cada subseção pega um pedaço do código Python existente e mostra o equivalente Go com explicação. Vamos começar pelo **núcleo (core)** porque ele não depende da UI e dá pra testar isolado.

---

### 5.1 ECS: Entity + Component + Registry (`ecs/`)

Recapitulando o Python (`core/entity/entity.py`):

```python
@dataclass
class Component: pass

class Entity:
    def __init__(self, name, entity_id=None):
        self.id = entity_id or str(uuid.uuid4())
        self.name = name
        self._components: dict[type, Component] = {}

    def add(self, comp): ...
    def get(self, comp_type): ...   # T | None
    def require(self, comp_type): ...  # T ou KeyError
```

**O desafio em Go:** Python guarda componentes num dict indexado por `type(comp)` e usa `cast` para devolver o tipo certo. Em Go, isso pede generics + um pouco de reflection.

**O salto de escalabilidade:** o pacote `ecs` resolve **três** coisas:

1. **`Entity` + `Add`/`AllComponents`** (struct + métodos).
2. **`Get[T]`/`Has[T]`/`Require[T]`** (funções genéricas com type parameters).
3. **Registry** — mapa global "nome do componente ↔ construtor". Cada arquivo de componente se cadastra via `init()`. Save/load usa o registry; **adicionar componente novo nunca exige editar nenhum outro arquivo.**

Pelo tamanho da coisa, separamos em três arquivos dentro de `ecs/`.

#### `internal/core/ecs/component.go` — interface + registry

```go
package ecs

import (
    "fmt"
    "reflect"
    "sync"
)

// Component é a interface "marcadora" que todo componente implementa.
// O método isComponent() é não-exportado (minúsculo): só tipos do MESMO
// pacote (ou que importem este e chamem o método) podem implementá-lo.
// Como o método é privado a este pacote, só tipos dentro de `ecs` poderiam
// implementá-lo diretamente... O TRUQUE: o pacote `components` declara
// `func (*X) isComponent() {}` — e como Go usa interface estrutural,
// basta ter o método para satisfazer a interface, mesmo se o nome do método
// for "privado" ao pacote `ecs`. Para isso funcionar, os componentes
// chamam um helper público (`ecs.MarkComponent`) — veja abaixo.
type Component interface {
    isComponent()
}

// MarkComponent é um helper sem efeito, usado APENAS para forçar que o método
// isComponent() seja chamado a partir do pacote ecs — garantindo que apenas
// tipos que importem ecs e usem este "selo" sejam considerados Component.
//
// Na prática, cada arquivo de componente embeda um campo `ecs.Marker` (struct
// vazia abaixo) que já carrega o método isComponent(). É a forma idiomática
// em Go de "interface fechada".
func MarkComponent() {}

// Marker é uma struct vazia que carrega o método isComponent().
// Cada componente concreto faz EMBEDDING dela:
//
//   type Identity struct {
//       ecs.Marker            // <- isso aqui satisfaz Component automaticamente
//       SocialClass string
//   }
//
// É o equivalente a herdar de uma classe-base vazia em Python, mas em Go
// se chama "embedding": Identity "tem" um Marker como campo anônimo, e
// herda seus métodos.
type Marker struct{}

func (Marker) isComponent() {}

// ---- Registry (auto-registro) ----

// Constructor é uma função zero-arg que devolve uma INSTÂNCIA vazia do
// componente, pronta para ser preenchida pelo json.Unmarshal.
// Sempre devolve PONTEIRO — porque save/load precisa de algo "mutável".
type Constructor func() Component

var (
    regMu      sync.RWMutex
    regByName  = make(map[string]Constructor)    // "Identity" -> func() Component
    nameByType = make(map[reflect.Type]string)   // reflect.TypeOf(Identity{}) -> "Identity"
)

// Register é chamada por cada arquivo de componente em seu init().
// Erra (com panic) se houver colisão de nome — colisão silenciosa seria
// pesadelo de debugar em save/load.
func Register(name string, ctor Constructor) {
    regMu.Lock()
    defer regMu.Unlock()
    if _, exists := regByName[name]; exists {
        panic(fmt.Sprintf("ecs.Register: nome duplicado %q", name))
    }
    regByName[name] = ctor
    // Pegamos o tipo "concreto" (sem o ponteiro) para podermos buscar
    // pelo tipo do valor armazenado.
    inst := ctor()
    t := reflect.TypeOf(inst)
    if t.Kind() == reflect.Ptr {
        t = t.Elem()
    }
    nameByType[t] = name
}

// NewByName devolve uma instância vazia do componente. Usado pelo loader
// para reconstruir saves.
func NewByName(name string) (Component, bool) {
    regMu.RLock()
    defer regMu.RUnlock()
    ctor, ok := regByName[name]
    if !ok {
        return nil, false
    }
    return ctor(), true
}

// NameOf devolve a string "Identity" a partir de um componente concreto.
// Usado pelo saver: ele percorre AllComponents() e serializa cada um com
// seu nome registrado, em vez de inferir do reflect.Type.Name() (que daria
// "Identity" também, mas via NameOf garante que SÓ componentes registrados
// são serializáveis).
func NameOf(c Component) (string, bool) {
    regMu.RLock()
    defer regMu.RUnlock()
    t := reflect.TypeOf(c)
    if t.Kind() == reflect.Ptr {
        t = t.Elem()
    }
    name, ok := nameByType[t]
    return name, ok
}

// RegisteredNames devolve todos os nomes registrados — útil para debug
// (CLI tool, testes que confirmam "todo componente que existe está registrado").
func RegisteredNames() []string {
    regMu.RLock()
    defer regMu.RUnlock()
    out := make([]string, 0, len(regByName))
    for n := range regByName {
        out = append(out, n)
    }
    return out
}
```

#### `internal/core/ecs/entity.go` — só a struct + métodos não-genéricos

```go
package ecs

import (
    "reflect"

    "github.com/google/uuid"
)

// Entity guarda id, nome e um mapa de componentes indexados pelo TIPO concreto.
// **Decisão chave:** o map armazena Component (interface) mas vamos SEMPRE
// inserir PONTEIRO (*Identity, *Vitality, etc). Isso faz mutações
// (`v.Energy--`) refletirem direto sem precisar re-Add.
type Entity struct {
    ID         string
    Name       string
    components map[reflect.Type]Component
}

// NewEntity é o "construtor". Convenção Go: NewX retorna *X.
// `id ...string` é variádico — equivale a parâmetro opcional do Python.
func NewEntity(name string, id ...string) *Entity {
    finalID := ""
    if len(id) > 0 && id[0] != "" {
        finalID = id[0]
    } else {
        finalID = uuid.NewString()
    }
    return &Entity{
        ID:         finalID,
        Name:       name,
        components: make(map[reflect.Type]Component),
    }
}

// Add insere/sobrescreve um componente. Normaliza pra usar SEMPRE o tipo
// "concreto" (sem ponteiro) como chave — assim Get[Identity] e Add(&Identity{})
// se entendem.
func (e *Entity) Add(c Component) *Entity {
    t := reflect.TypeOf(c)
    if t.Kind() == reflect.Ptr {
        t = t.Elem()
    }
    e.components[t] = c
    return e
}

// Remove é útil para systems que "removem capacidade" (ex: morte = remove Vitality).
func (e *Entity) Remove(t reflect.Type) {
    if t.Kind() == reflect.Ptr {
        t = t.Elem()
    }
    delete(e.components, t)
}

// AllComponents é usado pelo save. Devolve "NomeRegistrado -> Componente".
// Componentes não registrados são silenciosamente PULADOS — isso é
// proteção: se você criou um componente "temporário" pra debug e esqueceu
// de registrar, ele não vai parar no JSON.
func (e *Entity) AllComponents() map[string]Component {
    out := make(map[string]Component, len(e.components))
    for _, c := range e.components {
        if name, ok := NameOf(c); ok {
            out[name] = c
        }
    }
    return out
}
```

#### `internal/core/ecs/get.go` — funções genéricas

```go
package ecs

import (
    "fmt"
    "reflect"
)

// Get devolve (*T, true) se existir; (nil, false) se não.
// Repare no `*T` no retorno: como sempre armazenamos PONTEIRO,
// quem pegar pode mutar diretamente o componente.
//
// O type parameter `[T any]` é mais permissivo que `[T Component]` porque
// queremos T ser o tipo concreto (Identity), não o tipo do ponteiro (*Identity).
// A garantia de que o tipo é um Component vem do uso (você só consegue ter
// um *T no mapa se passou pelo Add, que aceita Component).
//
// Uso:  v, ok := ecs.Get[components.Vitality](e)
//       if ok { v.Energy-- }
func Get[T any](e *Entity) (*T, bool) {
    var zero T
    t := reflect.TypeOf(zero)
    c, ok := e.components[t]
    if !ok {
        return nil, false
    }
    typed, ok := c.(*T)
    return typed, ok
}

// Has só verifica existência, sem custo de cast.
func Has[T any](e *Entity) bool {
    var zero T
    _, ok := e.components[reflect.TypeOf(zero)]
    return ok
}

// Require é o equivalente do require() do Python: panic se não tiver.
// **Opinião:** prefira Get quando puder. Use Require só em invariantes
// que JAMAIS devem falhar (ex: World.MainPlayer() sempre tem Identity).
// Panic mata o programa — em jogo single-player não é tão ruim, em
// servidor seria catástrofe.
func Require[T any](e *Entity) *T {
    v, ok := Get[T](e)
    if !ok {
        var zero T
        panic(fmt.Sprintf("%s sem %T", e.Name, zero))
    }
    return v
}
```

**Coisas importantes pra fixar:**

1. **`Get` e `Has` não são métodos** — são funções top-level com generics. É uma limitação atual do Go: métodos não podem ter type parameters próprios. Por isso `ecs.Get[components.Vitality](e)` em vez de `e.Get[components.Vitality]()`.
2. **Sempre armazenamos PONTEIRO** dentro do mapa. Isso evita o bug clássico de "mutei a cópia" que mencionei na versão antiga. Mutação fica natural: `v.Energy--` simplesmente funciona.
3. **`Marker` (struct vazia embed)** é o jeito idiomático Go de fazer "herança de marcador". Você verá no §5.2 cada componente fazendo `ecs.Marker` como primeiro campo.
4. **O registry é populado por `init()`** nos arquivos de componente. Quando o programa começa, Go executa todos os `init()` antes do `main()` — o registry já está pronto quando o save/load roda.

---

### 5.2 Componentes: um arquivo por tipo (`components/`)

**A mudança de escalabilidade está aqui.** Cada componente vive em seu próprio arquivo, com **estrutura idêntica**:

```
internal/core/components/
├── identity.go        ← Identity + PlayerControl
├── vitality.go
├── location.go        ← Location + WorldKnowledge
├── personality.go
└── affinity.go
```

Adicionar um componente novo (`Hunger`, `Inventory`, `Skills`...) é **criar um arquivo seguindo o template**. Nada mais.

#### Template / regra do arquivo de componente

```go
package components

import "github.com/seuuser/dream-project/internal/core/ecs"

// 1) Struct com os campos. Embeda ecs.Marker pra implementar Component.
type Foo struct {
    ecs.Marker        `json:"-"`           // não serializa o marcador
    Bar         int   `json:"bar"`
    Baz         string `json:"baz"`
}

// 2) Construtor com defaults (opcional, mas recomendado).
func NewFoo() *Foo { return &Foo{Bar: 30} }

// 3) Métodos do componente (opcional).
func (f *Foo) DoSomething() { ... }

// 4) Auto-registro. Toda init() é chamada pelo Go ANTES do main().
func init() {
    ecs.Register("Foo", func() ecs.Component { return &Foo{} })
}
```

**Quatro regras, sempre na mesma ordem.** Quem ler qualquer arquivo do `components/` vê a mesma estrutura.

#### `internal/core/components/identity.go`

```go
package components

import "github.com/seuuser/dream-project/internal/core/ecs"

// Identity. Renomeei de IdentityComponent (Python) pra Identity —
// o sufixo "Component" vira ruído quando você já está no pacote `components`.
// Convenção Go: evitar "stuttering". `components.Identity` lê melhor que
// `components.IdentityComponent`.
type Identity struct {
    ecs.Marker  `json:"-"`
    SocialClass string `json:"social_class"`
    PublicName  string `json:"public_name"`
}

func NewIdentity(publicName string) *Identity {
    return &Identity{SocialClass: "comum", PublicName: publicName}
}

// PlayerControl: "marker component" — sem campos, só sinaliza
// "essa entidade é o player".
type PlayerControl struct {
    ecs.Marker `json:"-"`
}

func init() {
    ecs.Register("Identity", func() ecs.Component { return &Identity{} })
    ecs.Register("PlayerControl", func() ecs.Component { return &PlayerControl{} })
}
```

#### `internal/core/components/vitality.go`

```go
package components

import "github.com/seuuser/dream-project/internal/core/ecs"

type Vitality struct {
    ecs.Marker `json:"-"`
    Energy     int `json:"energy"`
    Cap        int `json:"cap"`
}

// NewVitality fornece os defaults do @dataclass(energy=30, cap=30).
// Go não tem "valor default por campo de struct" — construtores resolvem.
func NewVitality() *Vitality { return &Vitality{Energy: 30, Cap: 30} }

func init() {
    ecs.Register("Vitality", func() ecs.Component { return &Vitality{} })
}
```

#### `internal/core/components/personality.go`

```go
package components

import "github.com/seuuser/dream-project/internal/core/ecs"

// Archetype: tipo nomeado (string subjacente). MAIS SEGURO que string crua
// porque o compilador impede passar uma string qualquer como arquétipo.
type Archetype string

const (
    ArchetypeFriendly Archetype = "amigavel"
    ArchetypeGrumpy   Archetype = "rabugento"
    ArchetypeDevout   Archetype = "devoto"
    ArchetypeNeutral  Archetype = "neutro"
)

var ValidArchetypes = []Archetype{
    ArchetypeFriendly, ArchetypeGrumpy, ArchetypeDevout, ArchetypeNeutral,
}

type Personality struct {
    ecs.Marker `json:"-"`
    Archetype  Archetype `json:"archetype"`
    Mood       string    `json:"mood"` // "neutro" | "sereno" | "feliz" | "triste" | "irritado"
}

func NewPersonality() *Personality {
    return &Personality{Archetype: ArchetypeNeutral, Mood: "neutro"}
}

func init() {
    ecs.Register("Personality", func() ecs.Component { return &Personality{} })
}
```

> **Vai escalar mais?** Quando você tiver 20+ arquétipos e templates só pra eles, mude `var ValidArchetypes` pra **ser populado a partir de `data/dialogue/templates/*.json`** — a lista vira "todo arquivo dentro dessa pasta". Aí adicionar arquétipo é só criar JSON.

#### `internal/core/components/affinity.go`

```go
package components

import "github.com/seuuser/dream-project/internal/core/ecs"

type Affinity struct {
    ecs.Marker `json:"-"`
    ValueByID  map[string]int `json:"value_by_id"`
}

func NewAffinity() *Affinity {
    return &Affinity{ValueByID: make(map[string]int)}
}

// Adjust soma `delta`, faz clamp em [-100, 100], guarda e retorna o novo valor.
// Receiver `(a *Affinity)` por ponteiro porque vamos modificar o map.
func (a *Affinity) Adjust(otherID string, delta int) int {
    next := a.ValueByID[otherID] + delta  // zero-value se não existe
    if next > 100 {
        next = 100
    } else if next < -100 {
        next = -100
    }
    a.ValueByID[otherID] = next
    return next
}

func init() {
    ecs.Register("Affinity", func() ecs.Component { return &Affinity{} })
}
```

#### `internal/core/components/location.go`

```go
package components

import (
    "github.com/seuuser/dream-project/internal/core/ecs"
    "github.com/seuuser/dream-project/internal/core/geom"
)

type Location struct {
    ecs.Marker     `json:"-"`
    RegionName     string     `json:"region_name"`
    XY             geom.Coord `json:"xy"`
    InsideLocation bool       `json:"inside_location"`
    Room           geom.Coord `json:"room"`
}

// WorldKnowledge: o tipo aninhado mais hostil do projeto.
// Python: dict[str, dict[tuple[int,int], list[tuple[int,int]]]]
// Go: map[string]map[geom.Coord][]geom.Coord
//
// Em Go, MAP TEM QUE TER TIPO DE CHAVE COMPARÁVEL. Struct simples
// (sem slice/map dentro) é comparável — por isso geom.Coord serve como chave.
type WorldKnowledge struct {
    ecs.Marker     `json:"-"`
    KnownLocations map[string]map[geom.Coord][]geom.Coord `json:"known_locations"`
}

// Necessário porque o map zero-value é nil — escrever em map nil dá panic.
func NewWorldKnowledge() *WorldKnowledge {
    return &WorldKnowledge{
        KnownLocations: make(map[string]map[geom.Coord][]geom.Coord),
    }
}

func (k *WorldKnowledge) AddLocation(region string, xy geom.Coord) {
    if _, ok := k.KnownLocations[region]; !ok {
        k.KnownLocations[region] = make(map[geom.Coord][]geom.Coord)
    }
    if _, ok := k.KnownLocations[region][xy]; !ok {
        k.KnownLocations[region][xy] = []geom.Coord{}
    }
}

func (k *WorldKnowledge) AddRoom(region string, xy, roomXY geom.Coord) *WorldKnowledge {
    k.AddLocation(region, xy)
    k.KnownLocations[region][xy] = append(k.KnownLocations[region][xy], roomXY)
    return k
}

// Em Go não há `set`. Convenção: map[T]struct{}, ou só []T se a ordem não importa.
// `struct{}` ocupa 0 bytes — é o "ponto" que indica "presente".
func (k *WorldKnowledge) GetKnownPlaces(region string) map[geom.Coord]struct{} {
    out := make(map[geom.Coord]struct{})
    for xy := range k.KnownLocations[region] {
        out[xy] = struct{}{}
    }
    return out
}

func (k *WorldKnowledge) GetKnownRooms(region string, xy geom.Coord) map[geom.Coord]struct{} {
    out := make(map[geom.Coord]struct{})
    for _, r := range k.KnownLocations[region][xy] {
        out[r] = struct{}{}
    }
    return out
}

func init() {
    ecs.Register("Location", func() ecs.Component { return &Location{} })
    ecs.Register("WorldKnowledge", func() ecs.Component { return NewWorldKnowledge() })
}
```

E `internal/core/geom/coord.go`:

```go
// Package geom: tipos geométricos compartilhados, sem dependências.
package geom

// Coord substitui as tuplas (x, y) do Python. Struct nomeada é MUITO
// melhor que [2]int: você ganha c.X / c.Y em vez de c[0]/c[1], e o
// compilador te avisa se confundir "tamanho de grid" com "posição".
type Coord struct {
    X int `json:"x"`
    Y int `json:"y"`
}
```

#### Factory: junta componentes em entidades concretas

`internal/core/factory/player.go`:

```go
package factory

import (
    "github.com/seuuser/dream-project/internal/core/components"
    "github.com/seuuser/dream-project/internal/core/ecs"
)

func CreatePlayer(name string) *ecs.Entity {
    e := ecs.NewEntity(name)
    e.Add(components.NewIdentity(name))
    e.Add(components.NewVitality())
    e.Add(components.NewPersonality())
    e.Add(components.NewAffinity())
    e.Add(&components.Location{})
    e.Add(components.NewWorldKnowledge())
    e.Add(&components.PlayerControl{})
    return e
}
```

`internal/core/factory/npc.go`:

```go
package factory

import (
    "github.com/seuuser/dream-project/internal/core/components"
    "github.com/seuuser/dream-project/internal/core/ecs"
    "github.com/seuuser/dream-project/internal/core/geom"
)

// NPCOptions é o struct de "kwargs do Python".
// Quando construtores ganham 5+ parâmetros, criar um struct de options
// é mais legível que passar tudo posicional — quem chama vê os nomes.
type NPCOptions struct {
    Archetype      components.Archetype
    RegionName     string
    XY             geom.Coord
    InsideLocation bool
    RoomXY         geom.Coord
}

func CreateNPC(name string, opts NPCOptions) *ecs.Entity {
    if opts.Archetype == "" {
        opts.Archetype = components.ArchetypeNeutral
    }
    n := ecs.NewEntity(name)
    n.Add(components.NewIdentity(name))
    n.Add(components.NewVitality())
    n.Add(&components.Personality{Archetype: opts.Archetype, Mood: "neutro"})
    n.Add(components.NewAffinity())
    n.Add(&components.Location{
        RegionName:     opts.RegionName,
        XY:             opts.XY,
        InsideLocation: opts.InsideLocation,
        Room:           opts.RoomXY,
    })
    kn := components.NewWorldKnowledge()
    kn.AddRoom(opts.RegionName, opts.XY, opts.RoomXY)
    n.Add(kn)
    return n
}
```

**Uso:**

```go
player := factory.CreatePlayer("Aldo")
bertrand := factory.CreateNPC("Bertrand", factory.NPCOptions{
    Archetype: components.ArchetypeGrumpy,
    RegionName: "Kazer",
    XY: geom.Coord{X: 2, Y: 3},
    InsideLocation: true,
    RoomXY: geom.Coord{X: 0, Y: 0},
})
```

Lê bem, escala melhor: novo parâmetro no NPC = novo campo em `NPCOptions`, sem quebrar chamadas existentes (zero-value vira default).

#### Por que isso escala

| Operação | Antes (Python / arquivo único) | Agora (arquivo por componente) |
| --- | --- | --- |
| Adicionar componente novo | Mexer em `components/__init__.py` + criar `_x.py` + registrar em save/load | Criar `x.go` com 4 partes, `init()` faz todo o resto |
| Renomear um componente | Achar todo lugar que importa o nome | Compilador acha: rename em IDE refatora tudo |
| Save/load reconhece um novo? | Atualizar mapa central manual | Automático (registry pego pelo `init()`) |
| Listar todos os componentes (debug) | `dir(components_module)` | `ecs.RegisteredNames()` |
| Ter dois componentes com mesmo nome | Quebra silenciosa em load | `panic` no startup com mensagem clara |

---

### 5.3 Event Bus

O Python (`core/events/bus.py`) usa decorator `@event_bus.subscribe(EventType)` e identifica os eventos pelo `type(event)`. Em Go, fazer isso requer reflection. Existe alternativa **mais idiomática**: um bus por tipo de evento.

**Mas** como o projeto já tem múltiplos tipos e usar um bus por tipo daria um bus para cada (e mais código de boilerplate), eu vou manter um único bus com reflection. Vale o trade-off pela proximidade com o original.

#### `internal/core/events/bus.go`

```go
package events

import (
    "log"
    "reflect"
    "sync"
)

// Event é a interface marcadora. Igual ao Component.
type Event interface {
    isEvent()
}

// Handler é uma função que recebe um Event. Como recebe a interface genérica,
// o handler precisa fazer type assertion. Vamos esconder isso atrás de uma
// helper genérica (Subscribe[T]).
type Handler func(Event)

type EventBus struct {
    mu          sync.RWMutex                 // protege subscribers contra acesso concorrente
    subscribers map[reflect.Type][]Handler
}

func NewEventBus() *EventBus {
    return &EventBus{subscribers: make(map[reflect.Type][]Handler)}
}

// SubscribeRaw adiciona um handler "cru" (sem tipo específico).
// Use Subscribe[T] da função top-level abaixo em vez deste.
func (b *EventBus) SubscribeRaw(t reflect.Type, fn Handler) {
    b.mu.Lock()
    defer b.mu.Unlock()
    b.subscribers[t] = append(b.subscribers[t], fn)
}

// Publish chama todos os handlers registrados para o tipo do evento.
// Protege cada handler com recover() pra um erro em um não derrubar os outros
// — equivalente ao try/except do publish() em Python.
func (b *EventBus) Publish(ev Event) {
    b.mu.RLock()
    handlers := b.subscribers[reflect.TypeOf(ev)]
    // Copia local para soltar o lock antes de chamar — assim handler pode
    // publicar outros eventos sem deadlock.
    listeners := make([]Handler, len(handlers))
    copy(listeners, handlers)
    b.mu.RUnlock()

    for _, fn := range listeners {
        func() {
            defer func() {
                if r := recover(); r != nil {
                    log.Printf("subscriber falhou em %T: %v", ev, r)
                }
            }()
            fn(ev)
        }()
    }
}

func (b *EventBus) Clear() {
    b.mu.Lock()
    defer b.mu.Unlock()
    b.subscribers = make(map[reflect.Type][]Handler)
}

// Subscribe é a forma TIPADA de assinar um evento.
// Uso: events.Subscribe(bus, func(ev TimeAdvanced) { ... })
// O type parameter `T Event` é INFERIDO pelo Go a partir do argumento da função.
//
// É o que substitui o @event_bus.subscribe(TimeAdvanced) do Python.
func Subscribe[T Event](b *EventBus, fn func(T)) {
    var zero T
    t := reflect.TypeOf(zero)
    b.SubscribeRaw(t, func(ev Event) {
        // type assertion: dentro do bus o evento veio como Event, aqui sabemos que é T.
        if typed, ok := ev.(T); ok {
            fn(typed)
        }
    })
}

// Global, igual ao `event_bus` global do Python.
// **Opinião:** singletons globais facilitam migração mas atrapalham testes.
// Considere PASSAR o *EventBus como dependência (já que os sistemas e a UI
// recebem World — recebem bus também). Migre primeiro, refatore depois.
var Bus = NewEventBus()
```

#### `internal/core/events/types.go`

```go
package events

import "time"

// Cada evento é uma struct simples + método isEvent() de marcador.

type TimeAdvanced struct {
    Minutes     int
    NewDatetime time.Time
    Reason      string
    NewDay      bool
}

func (TimeAdvanced) isEvent() {}

type WorldLogMessage struct {
    Text    string
    Color   string
    Channel string
}

func (WorldLogMessage) isEvent() {}

type SpeechEmitted struct {
    NPCID      string
    NPCName    string
    Speech     string
    Intention  string
    TargetID   string  // "" significa "sem alvo" (em vez de None)
    Intensity  int
    LocationXY *Coord  // ponteiro para permitir nil (sem localização)
}

// Coord aqui é duplicado para não criar dependência cíclica com entity.
// Em Go, dependência cíclica entre pacotes NÃO COMPILA. Você lida com
// isso movendo o tipo compartilhado pra um pacote mais "embaixo" (ex:
// internal/core/geom/coord.go), ou duplicando se for trivial.
//
// **Opinião:** crie internal/core/geom/coord.go com Coord, e importe nos dois.
// Eu deixei duplicado aqui só pra você ver o sintoma.
type Coord struct{ X, Y int }

func (SpeechEmitted) isEvent() {}

type AffinityChanged struct {
    FromID   string
    ToID     string
    Delta    int
    NewValue int
}

func (AffinityChanged) isEvent() {}
```

**Uso (substituindo `@event_bus.subscribe(TimeAdvanced)`):**

```go
// Em Python:
//   @event_bus.subscribe(TimeAdvanced)
//   def _needs(ev: TimeAdvanced) -> None: ...
//
// Em Go:
events.Subscribe(events.Bus, func(ev events.TimeAdvanced) {
    // ... lógica ...
})
```

Note que **não há decorator**. Você chama `Subscribe` no momento certo. Normalmente isso vai num `RegisterX(world *World)` chamado uma vez quando o jogo começa.

---

### 5.4 Mundo, Região, Localização, Cômodo

Sem grandes surpresas estruturais; é tradução direta de `dataclass` + métodos.

#### `internal/core/world/room.go`

```go
package world

import "github.com/seuuser/dream-project/internal/core/geom"

// RoomType + tabela substituem ROOM_TYPES dict do Python.
// **Opinião:** mover o tipo para um "registry" tipado deixa o erro de digitar
// "qarto" virar erro de compilação. Pode ser uma melhoria pós-migração.
var roomTypes = map[string]struct {
    Glyph       string
    Color       string
    Description string
}{
    "sala":              {"*", "white", "Uma sala comum."},
    "quarto":            {"@", "yellow", "Um quarto comum."},
    "comodo_generico":   {"0", "orange", "Um lugar comum."},
}

type Room struct {
    XY       geom.Coord     `json:"xy"`
    RoomType string         `json:"room_type"`
    DataType map[string]any `json:"data_type"` // `any` = `interface{}` = qualquer coisa
}

// Property em Python vira método sem parâmetro em Go.
// Não há decorator @property; é só um método normal: room.Description()
func (r Room) Description() string {
    if t, ok := roomTypes[r.RoomType]; ok {
        return t.Description
    }
    return "Um lugar comum."
}

func (r Room) Glyph() string {
    if t, ok := roomTypes[r.RoomType]; ok {
        return t.Glyph
    }
    return "?"
}

func (r Room) Color() string {
    if t, ok := roomTypes[r.RoomType]; ok {
        return t.Color
    }
    return "white"
}
```

Para `Location` e `Region`, o padrão é o mesmo — slices em vez de listas, maps em vez de dicts. Vou pular para evitar repetição, mas tem dois pontos importantes:

#### Region.GenerateLocations: o aleatório ponderado

No Python:

```python
from random import choices
location_type = choices(types, weights=weights, k=1)[0]
```

Em Go, `math/rand` não tem `weighted_choice` pronto. Você escreve:

```go
import "math/rand"

// weightedChoice devolve um índice em [0, len(weights)) aleatório,
// ponderado por `weights`. Soma todos os pesos, sorteia um número
// até a soma, e percorre acumulando até passar.
func weightedChoice(weights []int) int {
    total := 0
    for _, w := range weights {
        total += w
    }
    r := rand.Intn(total) // [0, total)
    cum := 0
    for i, w := range weights {
        cum += w
        if r < cum {
            return i
        }
    }
    return len(weights) - 1
}
```

**Atenção:** desde Go 1.20, `math/rand` já é seedado automaticamente. Antes disso você precisava de `rand.Seed(time.Now().UnixNano())`. Como você vai usar Go novo, esqueça o seed manual. Se quiser segurança criptográfica, use `crypto/rand` (não é o caso aqui).

#### Construtor "factory method" classmethod

Python:

```python
@classmethod
def initial_city(cls, world_name: str) -> Self:
    inst = cls(world_name, name="Cidade Inicial")
    inst.composition = INITIAL_CITY_COMPOSITION
    inst.generate_locations()
    return inst
```

Go:

```go
// Não há @classmethod; é uma função top-level que devolve *Region.
func NewInitialCity(worldName string) *Region {
    r := &Region{
        WorldName:   worldName,
        Name:        "Cidade Inicial",
        Composition: initialCityComposition,
    }
    r.GenerateLocations(geom.Coord{X: 6, Y: 5})
    return r
}
```

Pronto. Sem `cls`, sem `Self`, sem `classmethod`. É só uma função.

---

### 5.5 Tempo

Python:

```python
class TimeManager:
    def __init__(self, world: World, step_minutes: int = 5) -> None:
        self.world = world
        self.step_min = step_minutes

    def _advance(self, minutes: int, reason: str) -> None:
        yesterday = self.world.time.date()
        self.world.time += timedelta(minutes=minutes)
        event_bus.publish(TimeAdvanced(...))
```

Go:

```go
package timemgr  // não pode chamar "time" porque conflita com o pacote padrão!

import (
    "time"

    "github.com/seuuser/dream-project/internal/core/events"
    "github.com/seuuser/dream-project/internal/core/world"
)

type Manager struct {
    World    *world.World
    StepMin  int
}

func New(w *world.World, stepMin int) *Manager {
    return &Manager{World: w, StepMin: stepMin}
}

// Now formata a hora atual do mundo. time.Time.Format usa um "layout"
// estranho: a data de referência é 2006-01-02 15:04:05.
// Não pergunte, só decora. O Go tem isso há anos.
func (m *Manager) Now() string {
    return m.World.Time.Format("02/01/2006 15:04")
}

// advance é o método privado (minúsculo) que faz o trabalho.
func (m *Manager) advance(minutes int, reason string) {
    yesterday := m.World.Time.YearDay()  // dia juliano: muda quando vira o dia
    // time.Time.Add aceita time.Duration. time.Minute é constante.
    m.World.Time = m.World.Time.Add(time.Duration(minutes) * time.Minute)
    events.Bus.Publish(events.TimeAdvanced{
        Minutes:     minutes,
        NewDatetime: m.World.Time,
        Reason:      reason,
        NewDay:      m.World.Time.YearDay() != yesterday,
    })
}

func (m *Manager) AdvanceInSteps(minutes int, reason string) {
    if minutes <= 0 {
        return
    }
    for i := 0; i < minutes; i++ {
        m.advance(1, reason)
    }
}
```

**Detalhe importante:** chamei o pacote de `timemgr` para não colidir com o pacote padrão `time`. Você pode chamar de `gametime`, `worldtime`, etc. **Dica:** ao colidir nomes, o que sempre funciona é alias no import (`import gtime "github.com/.../timemgr"`), mas o melhor é nomear bem o pacote.

---

### 5.6 Sistemas (vitalidade, diálogo) — auto-registro

#### `internal/core/systems/vitality.go`

Python:

```python
def register(world: World) -> None:
    @event_bus.subscribe(TimeAdvanced)
    def _needs(ev: TimeAdvanced) -> None:
        for entity in world.entities:
            v = entity.get(VitalityComponent)
            ...
```

Go:

```go
package systems

import (
    "github.com/seuuser/dream-project/internal/core/components"
    "github.com/seuuser/dream-project/internal/core/ecs"
    "github.com/seuuser/dream-project/internal/core/events"
    "github.com/seuuser/dream-project/internal/core/world"
)

// vitalitySystem é a função "registradora" desse sistema.
// Recebe o *World porque precisa assinar no Bus dele e iterar entidades.
func vitalitySystem(w *world.World) {
    events.Subscribe(w.Bus, func(ev events.TimeAdvanced) {
        for _, e := range w.Entities {
            // ecs.Get devolve *components.Vitality — mutação direta funciona,
            // sem precisar de e.Add(v) depois. Esse é o ganho do padrão
            // "componente sempre por ponteiro" do §5.1.
            v, ok := ecs.Get[components.Vitality](e)
            if !ok {
                continue
            }
            v.Energy -= ev.Minutes
            if v.Energy < 0 {
                v.Energy = 0
            }
        }
    })
}

// init() roda ANTES do main(). Aqui o sistema se auto-inscreve no registry
// abaixo. O `main` só precisa chamar systems.RunAll(world) — não precisa
// importar nem listar individualmente.
//
// Adicionar um sistema novo = criar novo arquivo systems/<nome>.go com:
//     func init() { Register(meuSistema) }
// Pronto. Zero edição central.
func init() {
    Register(vitalitySystem)
}
```

#### `internal/core/systems/registry.go` — auto-registro

Python tinha um `register_systems(world)` que listava cada sistema explicitamente. Em Go, cada sistema vira "self-registering" via `init()`. O registry só guarda a lista e roda no momento certo:

```go
package systems

import "github.com/seuuser/dream-project/internal/core/world"

// Setup é a assinatura de qualquer "system registrar": recebe o mundo,
// faz seus Subscribe no Bus, eventualmente guarda estado.
type Setup func(*world.World)

var registered []Setup

// Register é chamada por cada arquivo de sistema em init().
// **Importante:** chamadas em init() rodam ANTES do main(), e a ORDEM
// entre init() de arquivos diferentes do MESMO pacote é a ordem alfabética
// dos nomes de arquivo. Se você precisa de ordem específica, prefira chamar
// Register dentro de uma única função orquestradora — mas em geral sistemas
// independentes não se importam com ordem.
func Register(s Setup) {
    registered = append(registered, s)
}

// RunAll é chamada UMA VEZ pelo loop principal, depois que o World foi criado.
// Substitui o register_systems(world) do Python — mas a lista é populada
// automaticamente pelos init() dos arquivos individuais.
func RunAll(w *world.World) {
    for _, s := range registered {
        s(w)
    }
}
```

**Comparação rápida:**

| Antes (Python) | Agora (Go, com auto-registro) |
| --- | --- |
| `register_systems()` cresce a cada sistema novo | `RunAll()` nunca muda |
| Esquecer de adicionar a chamada = sistema silenciosamente morto | Impossível: o arquivo do sistema **é** o registro |
| Ordem importa? Você escreve manual | Use uma função orquestradora se precisar |
| Testar um sistema isolado | Importar o sistema sem rodar `init()`? Não, mas você pode criar `func vitalitySystemFor(w)` e testar diretamente sem registro |

> **Aviso sobre `init()`:** se você importa um pacote e ele tem `init()`, esse `init()` roda. Como `systems/` é importado pelo `main` (indiretamente, pelo `world` ou pela UI), todos os sistemas se registram automaticamente. Cuidado: importar um pacote SÓ pelo side-effect do `init()` precisa do "import em branco": `_ "github.com/.../systems"`. Em geral evite — se você precisa do pacote, importa normal.

---

### 5.7 Diálogo: pipeline, templates, intenções

#### Intention (enum)

Python tem `Intention(str, Enum)`. Go faz com tipo string + constantes:

```go
package dialogue

type Intention string

const (
    IntentionGreet     Intention = "CUMPRIMENTAR"
    IntentionPraise    Intention = "ELOGIAR"
    IntentionThreaten  Intention = "AMEACAR"
    IntentionFarewell  Intention = "DESPEDIR"
    IntentionNone      Intention = "NENHUMA"
)

type Result struct {
    Speech    string
    Intention Intention
    TargetID  string
    Intensity int
}
```

#### Templates

Estrutura idêntica ao dict aninhado do Python:

```go
package dialogue

import "math/rand"

var templates = map[string]map[Intention][]string{
    "amigavel": {
        IntentionGreet: {
            "Olá, {alvo}! Bom te ver.",
            "Ei, {alvo}! Tudo bem?",
        },
        IntentionPraise: {
            "{alvo}, você tem um jeito que ilumina o lugar.",
            "Sempre fico feliz de te ver, {alvo}.",
        },
        // ... resto igual
    },
    // ...
}

// GenerateSpeech escolhe um template aleatório e substitui {alvo} pelo nome.
// strings.ReplaceAll é o equivalente simples do .format(alvo=...)
func GenerateSpeech(archetype string, intention Intention, targetName string) string {
    block, ok := templates[archetype]
    if !ok {
        block = templates["neutro"]
    }
    variants, ok := block[intention]
    if !ok || len(variants) == 0 {
        return "..." + targetName + "."
    }
    chosen := variants[rand.Intn(len(variants))]
    if targetName == "" {
        targetName = "amigo"
    }
    return strings.ReplaceAll(chosen, "{alvo}", targetName)
}
```

#### Pipeline

```go
package dialogue

import (
    "math/rand"

    "github.com/seuuser/dream-project/internal/core/components"
    "github.com/seuuser/dream-project/internal/core/ecs"
    "github.com/seuuser/dream-project/internal/core/events"
    "github.com/seuuser/dream-project/internal/core/geom"
)

// Pipeline guarda dependências (Bus, RNG, etc) — facilita teste.
// Aqui está vazio porque o exemplo usa o Bus global; produção ideal:
// p := &Pipeline{Bus: world.Bus, Rng: rand.New(...)}
type Pipeline struct{}

func (p *Pipeline) DecideIntention(npc, target *ecs.Entity) Intention {
    affinity := 0
    if af, ok := ecs.Get[components.Affinity](npc); ok {
        affinity = af.ValueByID[target.ID]
    }
    switch {
    case affinity <= -50:
        return IntentionThreaten
    case affinity >= 30:
        return IntentionPraise
    default:
        return IntentionGreet
    }
}

func (p *Pipeline) Speak(npc, target *ecs.Entity, forced *Intention) Result {
    intent := IntentionNone
    if forced != nil {
        intent = *forced
    } else {
        intent = p.DecideIntention(npc, target)
    }

    archetype := string(components.ArchetypeNeutral)
    if pers, ok := ecs.Get[components.Personality](npc); ok {
        archetype = string(pers.Archetype)
    }

    speech := GenerateSpeech(archetype, intent, target.Name)
    intensity := rand.Intn(5) + 3 // [3..7]

    var locXY *geom.Coord
    if loc, ok := ecs.Get[components.Location](npc); ok {
        c := loc.XY
        locXY = &c
    }

    events.Bus.Publish(events.SpeechEmitted{
        NPCID: npc.ID, NPCName: npc.Name,
        Speech: speech, Intention: string(intent),
        TargetID: target.ID, Intensity: intensity,
        LocationXY: locXY,
    })

    return Result{
        Speech: speech, Intention: intent,
        TargetID: target.ID, Intensity: intensity,
    }
}
```

**Pequenos detalhes Go que aparecem aqui:**

- `forced *Intention` é como representar "opcional": ponteiro nulo = ausente. Você desreferencia com `*forced` para ler o valor.
- O `switch` com expressões `case x <= -50` substitui `if/elif`. Mais limpo.
- `string(pers.Archetype)` converte de `Archetype` (tipo) para `string` (subjacente). Necessário porque tipos nominalmente diferentes não se misturam, mesmo tendo o mesmo "shape".

#### Handlers

Equivalente a `register_dialogue_handlers`:

```go
package dialogue

import (
    "fmt"

    "github.com/seuuser/dream-project/internal/core/components"
    "github.com/seuuser/dream-project/internal/core/ecs"
    "github.com/seuuser/dream-project/internal/core/events"
    "github.com/seuuser/dream-project/internal/core/world"
)

var affinityDelta = map[Intention]int{
    IntentionThreaten: -1,
    IntentionPraise:   +1,
    IntentionGreet:    0,
    IntentionFarewell: 0,
    IntentionNone:     0,
}

var colorByIntention = map[Intention]string{
    IntentionThreaten: "red",
    IntentionPraise:   "green",
    IntentionGreet:    "cyan",
    IntentionFarewell: "dim",
    IntentionNone:     "white",
}

// RegisterHandlers é chamado pelo systems registry via init() — veja §5.6.
// Não tem nada de especial no diálogo; segue o mesmo padrão de qualquer sistema.
func RegisterHandlers(w *world.World) {
    events.Subscribe(w.Bus, func(ev events.SpeechEmitted) {
        if ev.TargetID == "" {
            return
        }
        target := w.GetEntity(ev.TargetID)
        sender := w.GetEntity(ev.NPCID)
        if target == nil || sender == nil {
            return
        }

        base := affinityDelta[Intention(ev.Intention)]
        if base == 0 {
            return
        }
        delta := base * ev.Intensity

        af, ok := ecs.Get[components.Affinity](target)
        if !ok {
            af = components.NewAffinity()
            target.Add(af)
        }
        newAf := af.Adjust(sender.ID, delta)

        w.Bus.Publish(events.AffinityChanged{
            FromID: target.ID, ToID: sender.ID,
            Delta: delta, NewValue: newAf,
        })
    })

    events.Subscribe(w.Bus, func(ev events.SpeechEmitted) {
        color := colorByIntention[Intention(ev.Intention)]
        if color == "" {
            color = "white"
        }
        w.Bus.Publish(events.WorldLogMessage{
            Text:    fmt.Sprintf("[%s][b]%s:[/b] %s[/]", color, ev.NPCName, ev.Speech),
            Color:   color,
            Channel: "dialogo",
        })
    })
}

// Auto-registro do system (mesmo padrão de vitalitySystem em §5.6).
func init() {
    systems.Register(RegisterHandlers)
}
```

> **Nota sobre `w.Bus`:** repare que o handler agora usa `w.Bus` em vez do `events.Bus` global. **Isso é parte da escalabilidade:** o `World` virou um container de dependências (Bus, RNG, TimeManager...). Em testes você cria um `World` com um Bus isolado — sem interferência entre testes. O global `events.Bus` continua existindo para compatibilidade temporária, mas a meta é eliminá-lo.

`fmt.Sprintf("%s", ...)` é o `f""` do Python. `%s` = string, `%d` = int, `%v` = qualquer coisa em formato default, `%T` = tipo. Tem mais; veja `go doc fmt`.

---

### 5.8 Save / Load

A migração mais delicada — porque envolve **reflection** para reconstruir componentes a partir do nome do tipo.

#### Save

A serialização é fácil: campos exportados são serializados automaticamente pelo `encoding/json`. As tags `json:"snake_case"` controlam o nome no JSON.

```go
package data

import (
    "encoding/json"
    "os"
    "path/filepath"
    "time"

    // Import em branco garante que TODOS os componentes registrem-se
    // antes que o save tente serializar — sem isso, AllComponents() ignoraria
    // tudo (porque NameOf devolve false).
    _ "github.com/seuuser/dream-project/internal/core/components"

    "github.com/seuuser/dream-project/internal/core/world"
)

const SchemaVersion = 1

type meta struct {
    SchemaVersion int    `json:"schema_version"`
    Parent        string `json:"parent"`
    Player        string `json:"player"`
    LocationType  string `json:"location_type"`
    Time          string `json:"time"`
}

type entityDTO struct {
    ID         string                     `json:"id"`
    Name       string                     `json:"name"`
    Components map[string]json.RawMessage `json:"components"`
    // json.RawMessage é uma "string JSON adiada": guarda os bytes do JSON
    // sem decodificar agora. Útil porque cada componente tem um tipo diferente.
}

// SaveGame escreve meta.json, world.json, entities.json em data/saves/<world-id>/<timestamp>/
// Retorna o timestamp usado (que vira o `parent_save` do mundo).
func SaveGame(w *world.World, baseDir string) (string, error) {
    timestamp := time.Now().Format("2006_1_2_15_4_5")
    saveDir := filepath.Join(baseDir, w.ID, timestamp)
    if err := os.MkdirAll(saveDir, 0o755); err != nil {
        return "", err
    }

    // ... lógica de meta (igual ao Python)

    // serializar entidades:
    entities := make([]entityDTO, 0, len(w.Entities))
    for _, e := range w.Entities {
        comps := make(map[string]json.RawMessage)
        for name, comp := range e.AllComponents() {
            raw, err := json.Marshal(comp)
            if err != nil {
                return "", err
            }
            comps[name] = raw
        }
        entities = append(entities, entityDTO{
            ID: e.ID, Name: e.Name, Components: comps,
        })
    }

    // escrever arquivos com indentação:
    if err := writeJSON(filepath.Join(saveDir, "entities.json"), entities); err != nil {
        return "", err
    }
    // ... mesma coisa para meta.json e world.json

    w.ParentSave = timestamp
    return timestamp, nil
}

func writeJSON(path string, v any) error {
    f, err := os.Create(path)
    if err != nil {
        return err
    }
    defer f.Close()
    enc := json.NewEncoder(f)
    enc.SetIndent("", "  ")  // indent=2 do Python
    enc.SetEscapeHTML(false) // ensure_ascii=False
    return enc.Encode(v)
}
```

**Pontos importantes:**

1. `error` é só um valor retornado, não exceção. **Toda função que pode falhar retorna `(resultado, error)`** e quem chama verifica `if err != nil`.
2. `defer f.Close()` agenda o fechamento para quando a função retornar — mesmo se der erro no meio. É o equivalente ao `with open(...)` do Python.
3. O padrão `0o755` é permissão Unix em octal (`rwxr-xr-x`).

#### Load (usa o registry — sem mapa hardcoded)

Aqui está a maior recompensa de ter `ecs.Register` em cada componente: **o load não precisa saber nada sobre os componentes existentes.** Ele só pergunta ao registry "tem um construtor pra esse nome?".

```go
package data

import (
    "encoding/json"
    "fmt"
    "os"
    "path/filepath"

    // **Import em branco:** importa o pacote SÓ pelo side-effect dos
    // init() — todos os componentes se registram no ecs.Registry.
    // Sem isto, o load tentaria desempacotar "Identity" e o registry
    // estaria vazio, dando "componente desconhecido".
    //
    // Esse é um dos POUCOS casos onde import em branco é a forma certa.
    _ "github.com/seuuser/dream-project/internal/core/components"

    "github.com/seuuser/dream-project/internal/core/ecs"
    "github.com/seuuser/dream-project/internal/core/world"
)

func componentFromJSON(name string, raw json.RawMessage) (ecs.Component, error) {
    inst, ok := ecs.NewByName(name)
    if !ok {
        return nil, fmt.Errorf("componente desconhecido no save: %q (registrado: %v)",
            name, ecs.RegisteredNames())
    }
    if err := json.Unmarshal(raw, inst); err != nil {
        return nil, fmt.Errorf("falha desserializando %s: %w", name, err)
    }
    return inst, nil
}

func LoadGame(worldID, timestamp, baseDir string) (*world.World, error) {
    saveDir := filepath.Join(baseDir, worldID, timestamp)

    var meta meta
    if err := readJSON(filepath.Join(saveDir, "meta.json"), &meta); err != nil {
        return nil, fmt.Errorf("meta: %w", err)
    }
    // ... ler world.json e entities.json idem ...

    // Para cada entidade do save, recria via ecs.NewEntity e popula:
    // for _, e := range entitiesDTO {
    //     ent := ecs.NewEntity(e.Name, e.ID)
    //     for name, raw := range e.Components {
    //         c, err := componentFromJSON(name, raw)
    //         if err != nil { return nil, err }
    //         ent.Add(c)
    //     }
    //     w.AddEntity(ent)
    // }
    return nil, os.ErrNotExist // placeholder
}

func readJSON(path string, dst any) error {
    f, err := os.Open(path)
    if err != nil {
        return err
    }
    defer f.Close()
    return json.NewDecoder(f).Decode(dst)
}
```

**Por que isso escala:**

| Cenário | Antes (mapa hardcoded) | Agora (registry) |
| --- | --- | --- |
| Adicionar componente | Editar `data/load.go` e adicionar entrada | `init()` no arquivo do componente já registra |
| Componente esquecido no save | Save grava, load erra silenciosamente | Erro claro no startup com lista do que TEM registrado |
| Remover componente | Editar o load pra não dar erro em saves antigos | Pode usar `_migrate` ou simplesmente ignorar nomes não conhecidos via flag |
| Testar load isoladamente | Mock do mapa | Import em branco de `components` em qualquer teste |

**Sobre `fmt.Errorf("... %w", err)`:** o `%w` envolve o erro original. Quem capturar pode usar `errors.Is(err, sentinel)` ou `errors.As(err, &alvo)` pra inspecionar a causa. É o equivalente "limpo" do `raise X from Y` do Python.

---

### 5.9 UI com Bubble Tea

Aqui está a maior mudança conceitual. Esqueça `compose()`, `mount()`, `query_one()`, callbacks via método. Bubble Tea é **funcional puro**: você tem um modelo (struct), uma função `Update` que recebe uma mensagem e devolve um novo modelo, e uma função `View` que renderiza o modelo em string.

#### A interface `tea.Model`

```go
type Model interface {
    Init() Cmd               // ação inicial (opcional). Cmd é uma função que produz Msg.
    Update(Msg) (Model, Cmd) // recebe mensagem (input, tick, etc), devolve novo Model
    View() string            // renderiza
}
```

É **basicamente Elm**. Toda interação (tecla, tick de timer, evento de janela, mensagem custom) chega no `Update` como uma `Msg`. Você decide o que fazer e devolve o novo estado + opcionalmente uma nova `Cmd` (efeito colateral).

#### App raiz (`internal/ui/app.go`)

```go
package ui

import (
    tea "github.com/charmbracelet/bubbletea"

    "github.com/seuuser/dream-project/internal/ui/screens"
)

// Screen é a interface que TODAS as telas implementam.
// Estende tea.Model adicionando um método "Title" — só para mostrar header.
type Screen interface {
    tea.Model
    Title() string
}

// App mantém uma pilha de telas, igual ao push_screen / pop_screen do Textual.
type App struct {
    stack []Screen
}

func NewApp() *App {
    return &App{stack: []Screen{screens.NewMenu()}}
}

func (a *App) Init() tea.Cmd {
    return a.current().Init()
}

func (a *App) current() Screen { return a.stack[len(a.stack)-1] }

// Update repassa para a tela atual e lida com mensagens de "navegação"
// que podem trocar a tela.
func (a *App) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
    switch m := msg.(type) {
    case screens.PushMsg:
        a.stack = append(a.stack, m.Screen)
        return a, m.Screen.Init()
    case screens.PopMsg:
        if len(a.stack) > 1 {
            a.stack = a.stack[:len(a.stack)-1]
        }
        return a, nil
    case tea.KeyMsg:
        if m.String() == "ctrl+c" {
            return a, tea.Quit
        }
    }
    newScreen, cmd := a.current().Update(msg)
    a.stack[len(a.stack)-1] = newScreen.(Screen)
    return a, cmd
}

func (a *App) View() string {
    return a.current().View()
}

// Para abrir uma tela de qualquer lugar, retorne uma PushMsg como Cmd.
```

#### `internal/ui/screens/menu.go`

```go
package screens

import (
    tea "github.com/charmbracelet/bubbletea"
    "github.com/charmbracelet/lipgloss"
)

type Menu struct {
    cursor int
    items  []string
}

func NewMenu() *Menu {
    return &Menu{items: []string{"Novo Jogo", "Carregar Jogo", "Sair"}}
}

func (m *Menu) Title() string { return "Menu" }
func (m *Menu) Init() tea.Cmd { return nil }

func (m *Menu) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
    switch msg := msg.(type) {
    case tea.KeyMsg:
        switch msg.String() {
        case "up", "k":
            if m.cursor > 0 {
                m.cursor--
            }
        case "down", "j":
            if m.cursor < len(m.items)-1 {
                m.cursor++
            }
        case "enter":
            return m, m.activate()
        }
    }
    return m, nil
}

func (m *Menu) activate() tea.Cmd {
    switch m.items[m.cursor] {
    case "Novo Jogo":
        return func() tea.Msg { return PushMsg{Screen: NewNewGame()} }
    case "Carregar Jogo":
        return func() tea.Msg { return PushMsg{Screen: NewLoadGame()} }
    case "Sair":
        return tea.Quit
    }
    return nil
}

var (
    titleStyle    = lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("11"))
    selectedStyle = lipgloss.NewStyle().Reverse(true)
)

func (m *Menu) View() string {
    var b strings.Builder
    b.WriteString(titleStyle.Render("DREAM PROJECT") + "\n")
    b.WriteString("um RPG textual de mundo vivo\n\n")
    for i, item := range m.items {
        line := item
        if i == m.cursor {
            line = selectedStyle.Render("> " + item)
        } else {
            line = "  " + item
        }
        b.WriteString(line + "\n")
    }
    return b.String()
}

// Mensagens de navegação:
type PushMsg struct{ Screen Screen }
type PopMsg struct{}
```

**O que mudou comparado ao Textual:**

| Textual (Python) | Bubble Tea (Go) |
| --- | --- |
| `compose()` devolve widgets, montagem é mágica | `View()` retorna string, você controla tudo |
| `on_button_pressed` (callback por método) | `Update()` switch por tipo de Msg |
| `self.app.push_screen(X)` (efeito direto) | `return func() tea.Msg { return PushMsg{...} }` (Cmd retornado) |
| CSS file separado (`app.tcss`) | Lipgloss styles in-code |
| `self.set_interval(0.4, fn)` para timers | `tea.Tick(time.Millisecond * 400, ...)` retorna Cmd |
| `event_bus.publish` chega no widget via subscribe | Você lê do event bus no `Update()` via `tea.Msg` custom |

**A maior pegadinha:** Bubble Tea é **single-thread** no `Update`. Toda mensagem é processada em sequência. Para efeitos assíncronos (ticks de tempo, eventos do bus), você retorna `Cmd`s — funções que rodam em goroutines e produzem `Msg`s que voltam pro `Update`.

#### Conectando o EventBus à UI

Como o EventBus publica sincronamente, e Bubble Tea só age via `Msg`, a ponte é:

```go
// Cria um channel que recebe eventos. Inscreve no bus colocando-os no channel.
// Retorna um Cmd que lê do channel e emite como tea.Msg.
type LogMsg events.WorldLogMessage

func ListenWorldLog(bus *events.EventBus, ch chan events.WorldLogMessage) tea.Cmd {
    events.Subscribe(bus, func(ev events.WorldLogMessage) {
        // Non-blocking: se ninguém estiver lendo, joga fora (ou faz buffer maior)
        select {
        case ch <- ev:
        default:
        }
    })
    return func() tea.Msg {
        return LogMsg(<-ch)
    }
}

// Na tela do jogo, no Update, você recebe LogMsg e atualiza o log.
// Depois de processar, retorne uma nova Cmd que volta a esperar do channel:
//   return m, ListenAgain(ch)
```

Vou parar por aqui de UI para não ficar enorme — quando você chegar nesse ponto da migração, eu posso destrinchar tela por tela. **O importante agora é o modelo mental:** `Update` é puro, `View` é puro, efeitos colaterais voltam como Msg via Cmd.

---

## Erros, em vez de exceções

Esta é a parte que mais incomoda quem vem de Python. Não há `try/except`. Cada operação que pode falhar retorna um `error`, e você verifica.

```go
// Python:
//   try:
//       world = load_game(world_id, ts)
//   except Exception as e:
//       self.notify(f"Falha ao carregar: {e}", severity="error")

// Go:
world, err := data.LoadGame(worldID, ts, "data/saves")
if err != nil {
    return m, notify(fmt.Sprintf("Falha ao carregar: %v", err))
}
// ... usar world ...
```

**Padrões que vão te economizar dor:**

1. **Não ignore erros.** Mesmo que pareça impossível, escreva `_ = err` ou comente o porquê.
2. **Embrulhe contexto:** `fmt.Errorf("falha desserializando %s: %w", name, err)`. O `%w` mantém a cadeia. Quem chama pode usar `errors.Is(err, sentinelErr)` ou `errors.As(err, &alvoTyped)`.
3. **`panic` é para "isso nunca deve acontecer"** (asserts internas, programação defensiva). Não use para fluxo normal. O `assert` do Python vira ou `if x == nil { panic(...) }` se for invariante, ou `if x == nil { return nil, errors.New(...) }` se for erro recuperável. Use o segundo quase sempre.
4. **`defer` para limpeza.** É como o `finally` do Python, mas amarrado à função inteira, não a um bloco. Use para `Close()`, `Unlock()`, etc.

---

## Concorrência: goroutines, channels e ticks de tempo

Você vai precisar disso só quando começar a UI (timers de tempo) e os "eventos do mundo no background". Resumo do essencial:

```go
// goroutine = "thread leve". O Go schedula milhares delas em poucas threads de OS.
go fazerCoisa()  // chama fazerCoisa() em paralelo, retorna imediatamente

// channel = canal tipado para comunicação entre goroutines
ch := make(chan int, 10)  // buffer de 10
go func() {
    ch <- 42  // envia
}()
v := <-ch     // recebe (bloqueia até alguém enviar)

// select = switch para channels
select {
case v := <-ch1:
    // recebeu de ch1
case ch2 <- 99:
    // enviou em ch2
case <-time.After(time.Second):
    // timeout
default:
    // não bloqueia se nenhum estiver pronto
}
```

**Dica de ouro:** no Bubble Tea, **não compartilhe estado entre o seu `Model` e goroutines**. Toda mudança de estado deve voltar como `tea.Msg`. Use channels só para "trazer eventos externos para dentro do loop do Bubble Tea".

---

## Roadmap sugerido (ordem de migração)

Não migre tudo de uma vez. Vai por camadas, e mantenha o Python rodando até a paridade.

1. **`go.mod` + `main.go` na raiz** que só imprime "hello". Confirme que builda com `go run .`.
2. **`geom/coord.go`** primeiro — todo o resto depende dele.
3. **`ecs/` completo** (Entity, Component, Marker, registry, generics). Teste round-trip: criar entidade, Add, Get, NameOf, NewByName. Sem isso, nada funciona.
4. **`components/` com 2 componentes** (Identity, Vitality) usando o template do §5.2. Teste que `init()` registra. Adicione os outros 3 quando o padrão estiver na cabeça.
5. **`events/` (Bus + 1 tipo de evento).** Teste publish/subscribe tipado.
6. **`world/`** (Room, Location, Region, World — World já com `Bus *events.EventBus`).
7. **`factory/`** + **`timemgr/`** + sistema de **vitalidade** com auto-registro via `init()`. Já dá pra simular "passou 5 minutos" e ver a energia caindo.
8. **`dialogue/`** (templates, pipeline, handlers). Mantenha templates inline; depois move pra JSON.
9. **`data/` save+load** com JSON. Faça round-trip: salvar, carregar, comparar igualdade. Esse é o melhor teste de que o registry está fazendo seu papel.
10. **UI mínima com Bubble Tea**: menu → new game → tela vazia com mapa renderizado em texto. Adiciona movimento.
11. **UI completa**: status, world log, environment analysis, modais.
12. **Data-driven content**: move `LOCATION_TYPES`, `ROOM_TYPES`, `TEMPLATES` pra arquivos JSON. Veja §10.

**Em cada passo, escreva pelo menos um `_test.go`.** Sério, Go testa MUITO bem e MUITO rápido. Você vai economizar horas de debugging.

---

## Opiniões e dicas práticas

**Coisas que eu mudaria na arquitetura ao migrar** (algumas já estão refletidas na estrutura do §3):

1. **Pare de usar o bus global.** Passe `*EventBus` como dependência (via `world.Bus`). Vai facilitar testes e evita aquele `event_bus.clear()` no início de cada partida.
2. **Faça `*World` carregar o `*EventBus`.** Em Python eles vivem separados; em Go, deixe o `World` ser o "container" de tudo (`world.Bus`, `world.Time`, `world.Rng`, etc).
3. **Repense `Require`.** Em Go, panic por componente faltando é hostil. Prefira retornar `(*T, bool)` e propagar a decisão. Só use `Require` em invariantes verdadeiras (ex: `World.MainPlayer()` deveria sempre existir).
4. **Não traduza mixin como embedding cegamente.** `MovementMixin` em Python é meio cheirinho de "código que não soube onde morar". Em Go, faça uma função `Move(ctx, dir)` que recebe os ponteiros que precisa. Resolve sem mistério.

**Coisas a NÃO fazer:**

- **Não invente sua própria `Optional[T]`.** Go é `(T, bool)` para "talvez" e `*T` para "opcional mutável". Já é o suficiente.
- **Não use reflection para tudo.** Cada `reflect.TypeOf` deixa o código mais lento e menos legível. Use só onde realmente precisa (registry de componentes, save/load genérico).
- **Não chame `panic()` para lidar com erro do usuário.** Erros do mundo real (arquivo não existe, save corrompido) viram `error`. Panic é última instância.
- **Não use `interface{}` (ou `any`) sem necessidade.** Você perde a tipagem e cai num cast a cada uso. Generics resolve 90% dos casos onde você teria usado.

**Ferramentas que valem instalar:**

- `gopls` — language server (autocomplete, refactor).
- `golangci-lint` — linter "guarda-chuva". Roda a cada commit. (`golangci-lint run ./...`)
- `gotestsum` — visualizador de testes mais bonito.
- `air` — hot-reload pra dev (`air` na raiz, ele recompila a cada save).

**Comando que eu uso 50x por dia:**

```bash
go test ./... && go vet ./... && go build ./...
```

Se isso passar, você está bem.

---

## 10. Padrões de escalabilidade

Esta seção é o **resumo conceitual** do que aparece espalhado pelo README. Quando você for adicionar feature nova, releia isso primeiro — vai poupar refactor mais tarde.

### 10.1 Regra de ouro: "adicionar é criar um arquivo"

A pergunta certa pra cada novo conceito é: **"adicionar mais um custa quanto?"**

| Conceito | Custo de adicionar um novo |
| --- | --- |
| Componente | 1 arquivo em `components/`, segue template do §5.2 |
| Sistema | 1 arquivo em `systems/`, `init() { Register(fn) }` |
| Evento | 1 struct em `events/<dominio>.go`, com método `isEvent()` |
| Arquétipo de NPC | 1 JSON em `data/dialogue/templates/` (depois de §10.4) |
| Tipo de localização | 1 entrada em `data/world/locations.json` |
| Tela de UI | 1 arquivo em `ui/screens/`, struct implementando `tea.Model` + `Title()` |

**Se a resposta for "tenho que editar uma lista central", está errado.** Repensar.

### 10.2 Auto-registro via `init()`

Padrão repetido em **3 lugares**: components, systems, e (futuramente) handlers de comando/UI. O esqueleto é sempre:

```go
package fulano

// 1) tipo
type Fulano struct { ... }

// 2) construtor
func newFulano(...) *Fulano { ... }

// 3) método de auto-registro
func init() {
    registry.Register("nome-único", func() *Fulano { return newFulano(...) })
}
```

**Vantagens:**

- Adicionar = criar arquivo. Sem `__init__.py`-like central.
- Renomear = compilador acha tudo (rename refactor da IDE refatora limpo).
- Esquecer de registrar = impossível, está no mesmo arquivo do tipo.

**Cuidados:**

- A ordem entre `init()`s de arquivos **diferentes do mesmo pacote** é alfabética por nome de arquivo. Em geral, não dependa de ordem.
- Em testes, lembre de importar o pacote (mesmo que com `_ "..."` em branco) pra disparar os `init()`s — senão o registry está vazio.

### 10.3 Dependency injection via `World` (sem singletons)

**O que NÃO queremos:**

```go
events.Bus.Publish(...)        // ruim: global, escala mal em testes
rand.Intn(...)                 // ruim: PRNG global, testes ficam não-determinísticos
time.Now()                     // ruim: testes não podem "viajar no tempo"
```

**O que queremos:**

```go
type World struct {
    ID         string
    Name       string
    Entities   []*ecs.Entity
    Regions    []*Region
    Time       time.Time

    Bus *events.EventBus  // bus dedicado ao mundo — em teste é outro
    Rng *rand.Rand        // PRNG seedável — em teste, seed fixo = teste determinístico
    Now func() time.Time  // func injetável — em teste, retorna data controlada
}

func NewWorld(name string, opts ...WorldOption) *World {
    w := &World{
        ID:   uuid.NewString(),
        Name: name,
        Bus:  events.NewEventBus(),
        Rng:  rand.New(rand.NewSource(time.Now().UnixNano())),
        Now:  time.Now,
    }
    for _, opt := range opts {
        opt(w)
    }
    return w
}

// Functional options: padrão Go pra construtor flexível sem 10 parâmetros.
type WorldOption func(*World)

func WithRng(r *rand.Rand) WorldOption    { return func(w *World) { w.Rng = r } }
func WithClock(now func() time.Time) WorldOption { return func(w *World) { w.Now = now } }
```

**Por que isso escala:** todo handler, todo sistema, toda função que precisa de "ambiente" recebe `*World` (ou as partes dele). Em teste, você cria um World com PRNG fixo (`rand.New(rand.NewSource(42))`) e relógio congelado (`func() time.Time { return testDate }`). Mesmo input → mesmo output, sempre.

### 10.4 Conteúdo em dados, não em código

Os dicts hardcoded são o teto de escalabilidade do projeto Python:

- `ROOM_TYPES`, `LOCATION_TYPES` em `room.py`/`location.py`
- `TEMPLATES` (diálogo) em `templates.py`
- `VALID_ARCHETYPES` em `_personality.py`
- `INITIAL_CITY_COMPOSITION` em `region.py`

**Por que dói:** adicionar um tipo de cômodo "cozinha" exige recompilar. Pior, conteúdo de game design (textos, balanceamento) fica preso entre lógica de código.

**Como ficar escalável:**

```
data/
├── world/
│   ├── locations.json      # tipos de localizações: glyph, color, description
│   └── rooms.json          # idem para cômodos
├── dialogue/
│   └── templates/
│       ├── amigavel.json   # 1 arquivo por arquétipo
│       ├── rabugento.json
│       └── ...
└── world/
    └── cities/
        └── inicial.json    # composition + tamanho
```

E o carregamento no Go:

```go
package roomtypes

import (
    "embed"           // embeda os JSONs no binário — sem dependência de filesystem em runtime
    "encoding/json"
)

//go:embed data/*.json
var fs embed.FS

type RoomTypeDef struct {
    Glyph       string `json:"glyph"`
    Color       string `json:"color"`
    Description string `json:"description"`
}

var Types map[string]RoomTypeDef

func init() {
    raw, err := fs.ReadFile("data/rooms.json")
    if err != nil { panic(err) }
    if err := json.Unmarshal(raw, &Types); err != nil { panic(err) }
}
```

**O `embed.FS`** é uma feature poderosa do Go: o conteúdo do arquivo vai **dentro do binário**. Você continua tendo "binário único" para distribuir. Para o **dev**, edite o JSON e rode `go run .` — o `embed` re-lê do disco no build.

> **Quando NÃO embedar:** se quiser que o usuário possa modificar conteúdo sem recompilar (mod support), aí carrega de filesystem real. Pra você no início, embed é melhor.

### 10.5 Camadas testáveis isoladamente

Cada pacote em `internal/core/` deve ter um teste que **não importa nenhum outro pacote do projeto** (exceto `geom`). Isso prova que as camadas estão desacopladas.

```
ecs/        → testa Entity, Register, Get, NameOf — só importa testing + reflect
components/ → testa cada componente isoladamente — importa ecs
events/     → testa Bus + Subscribe[T] — só importa testing
world/      → testa World + Region + ... — importa events, ecs, components, geom
systems/    → testa cada sistema com um World fake — importa world, events, components
```

**Se um teste de `ecs/` precisa importar `world/`, algo está errado.** O fluxo de dependências deve ser **descendente sempre**: UI depende de world depende de systems depende de events/ecs/components depende de geom. Nunca o oposto.

### 10.6 Convenções de nomes que ajudam

- **Não repita o nome do pacote no tipo.** `components.Identity` (não `components.IdentityComponent`). `events.SpeechEmitted` (não `events.SpeechEmittedEvent`).
- **`New<Tipo>` para construtor** que devolve `*Tipo` com defaults. Sem isso, o caller precisa lembrar dos valores padrão.
- **Funções genéricas com nome curto** se o pacote é descritivo: `ecs.Get[T]`, `ecs.Has[T]`. Não `ecs.GetComponent[T]` — redundante.
- **Métodos de "verificar" começam com `Is`/`Has`/`Can`:** `IsAlive`, `HasAffinity`, `CanMove`. Lê-se como inglês.
- **Erros sentinela são `Err<Coisa>`:** `var ErrNotFound = errors.New("...")`. Permite `errors.Is(err, ErrNotFound)`.

### 10.7 Quando partir um pacote em dois

Sinais de que `pacote/foo.go` precisa virar `pacote/foo/`:

- Arquivo passa de ~400 linhas de código (não conta comentários).
- Surgem 2+ tipos que não se referenciam, no mesmo arquivo.
- Você está duplicando lógica entre arquivos do mesmo pacote.
- Os testes ficaram muito grandes pra navegar.

**Mas não parta cedo demais.** Pacotes Go pequenos com poucos arquivos são melhores que árvore de subpacotes raso e cheia de import-cycle dance.

---

## Apêndice: cheat-sheet de tradução

```
Python                                  Go
─────────────────────────────────────── ────────────────────────────────────────
str(uuid.uuid4())                       uuid.NewString()
datetime.now()                          time.Now()
datetime(1000,1,1,7,0)                  time.Date(1000,1,1,7,0,0,0,time.UTC)
date + timedelta(minutes=5)             date.Add(5 * time.Minute)
list[T]                                 []T
dict[K,V]                               map[K]V
set[T]                                  map[T]struct{}
tuple[int,int]                          struct{ X, Y int } (ou [2]int)
None                                    nil
[x for x in xs if pred(x)]              for _, x := range xs { if pred(x) { ... } }
next((x for x in xs if p(x)), None)     for _, x := range xs { if p(x) { return x } }
                                        return nil   // (sem expression-style)
json.dumps(x, indent=2)                 json.MarshalIndent(x, "", "  ")
json.loads(s)                           json.Unmarshal([]byte(s), &v)
open(path).read()                       os.ReadFile(path)
open(path,"w").write(s)                 os.WriteFile(path, []byte(s), 0o644)
Path(p).mkdir(parents=True)             os.MkdirAll(p, 0o755)
shutil.rmtree(p)                        os.RemoveAll(p)
f"{a}/{b}/{c}"                          fmt.Sprintf("%s/%s/%s", a, b, c)
                                        ou: path/filepath.Join(a, b, c)
str.split(",")                          strings.Split(s, ",")
",".join(xs)                            strings.Join(xs, ",")
str.replace(a, b)                       strings.ReplaceAll(s, a, b)
str.startswith(p)                       strings.HasPrefix(s, p)
random.randint(a, b)                    a + rand.Intn(b-a+1)
random.choice(xs)                       xs[rand.Intn(len(xs))]
@dataclass                              type X struct { ... }
@property                               func (x X) Name() ...
@classmethod                            func NewX(...) X
try/except                              if err != nil { ... }
raise                                   return err   (panic só em catástrofes)
with open(...) as f:                    f, _ := os.Open(...); defer f.Close()
```

---

**Boa migração. Vai ser desconfortável nas primeiras 2 semanas e libertador depois.** Quando bater alguma dúvida específica em algum trecho, pode trazer o pedaço Python que eu desenho o equivalente Go com a explicação no mesmo formato deste README.
