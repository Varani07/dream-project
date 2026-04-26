# Passo a Passo: Integração com LLM Local Cuidadosamente

Como o uso de LLM para falas de NPC pode destruir o FPS, ele será feito em Background (Assíncrono) usando a biblioteca Open Source `llama-cpp-python`, que permite carregar um modelo pequeno (ex: um modelo Llama3 8B Quantizado).

## 1. Instalação e Preparação
Não vamos usar serviços pagos como OpenAI.
1. No terminal: `pip install llama-cpp-python`
2. Baixe um arquivo modelo (`.gguf`) minúsculo focado em conversas pelo *HuggingFace* (ex: Llama-3-8B-Instruct.Q4_K_M.gguf) e ponha na pasta raiz.

## 2. Código: O Gerador de Falas
O truque não é pedir para a IA jogar o jogo, mas sim gerar o texto a partir de uma "Memória Estruturada".

```python
# integracao_llm.py
from llama_cpp import Llama
import asyncio

class DialogueManager:
    def __init__(self, model_path):
        # Carregamos o modelo. n_ctx controla a janela de contexto.
        # Só é instanciado UMA VEZ quando o jogo abre para não pesar.
        self.llm = Llama(model_path=model_path, n_ctx=512, verbose=False)
        
    async def generate_npc_speech_async(self, npc_name, npc_personality, memory_tags, situation):
        """
        Roda a geração num executor para não travar a interface do jogo (o Textual).
        """
        prompt = f"""
        Você é um personagem de RPG chamado {npc_name}.
        Personalidade: {npc_personality}.
        O que você sabe (Fatos): {memory_tags}.
        A situação atual é: {situation}.
        Fale uma frase curta que reflita isso, sem narrar ações, apenas a sua fala.
        """
        
        # Roda a função síncrona do llama em uma thread em background
        loop = asyncio.get_event_loop()
        resposta = await loop.run_in_executor(None, self._run_llm, prompt)
        return resposta

    def _run_llm(self, prompt):
        # Gera o texto limitando a 50 tokens (muito rápido)
        output = self.llm(prompt, max_tokens=50, stop=["\n", "User:"], echo=False)
        return output['choices'][0]['text'].strip()
```

## 3. Invocação Cautelosa
No seu script, só chame o LLM quando for **estritamente necessário**, ou seja, num encontro de relevância ou com alta afinidade, e nunca a cada 5 segundos.

```python
import asyncio

async def encontro_no_local(player, npc):
    print(f"Você se aproximou de {npc.name}.")
    
    # Montando as tags do que o NPC acha do player
    relacionamento = "Neutro"
    if "roubou_faca" in npc.memories.get(player.id, []):
        relacionamento = "Odeia o jogador"

    # Não trava a tela! O textual pode exibir "Pensando..."
    print("Gerando diálogo (não travando a tela)...")
    
    # Chama o LLM
    dm = DialogueManager("modelo-pequeno.gguf") 
    fala = await dm.generate_npc_speech_async(
        npc_name=npc.name,
        npc_personality="Rabugento",
        memory_tags=relacionamento,
        situation="O jogador entrou na sua forja."
    )
    
    # Exibe no Textual
    print(f"{npc.name} diz: '{fala}'")

# Executaria com asyncio.run(encontro_no_local(...)) no loop do jogo
```

### Dica de Otimização
Use um **Cache**: se um NPC genérico ("Camponês") ver a situação "Jogador passou", e o cache já tiver uma fala "Olá, forasteiro", recicle essa fala sem usar a IA.
