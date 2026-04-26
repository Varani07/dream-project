# Passo a Passo: Ações, Tempo e Interrupção

A passagem do mundo não precisa (nem deve) rodar a 60 frames por segundo consumindo a CPU. Ela é um "avanço rápido" de relógio engatilhado pelas ações do jogador.

## 1. O Loop de Passagem de Tempo
Quando o jogador executa "Trabalhar (4 horas)", o sistema processa blocos de tempo menores para dar chance aos NPCs de agirem ou do evento ser interrompido.

```python
import time

class TimeManager:
    def __init__(self):
        self.current_time_minutes = 0

    def start_action(self, action_name, duration_minutes, player):
        print(f"Iniciando {action_name}. Duracao: {duration_minutes}m")
        
        minutes_passed = 0
        step = 5  # Avançamos o mundo a cada 5 minutos na simulação
        
        while minutes_passed < duration_minutes:
            # 1. Avança o tempo
            self.current_time_minutes += step
            minutes_passed += step
            
            # 2. Roda a lógica de todos os NPCs e Eventos do Mundo para este "step"
            event_triggered = self.simulate_world_step(step)
            
            # 3. Interrupção!
            if event_triggered:
                print(f"Ação interrompida após {minutes_passed}m devido a um evento!")
                return {"status": "interrupted", "minutes_spent": minutes_passed}
        
        # Ação concluída com sucesso
        print("Ação finalizada!")
        return {"status": "completed", "minutes_spent": duration_minutes}

    def simulate_world_step(self, step_minutes):
        # Aqui iteramos sobre NPCs, rolando as probabilidades de encontros/eventos
        import random
        
        # Exemplo de interrupção com 2% de chance a cada 5 minutos
        if random.random() < 0.02:
            return True # Ocorreu um evento que para o tempo!
        return False
```

## 2. Consumo de Energia
Antes da ação iniciar, verificamos se a Entidade (Player/NPC) possui o atributo de energia.

```python
class Entity:
    def __init__(self, name, max_energy):
        self.name = name
        self.energy = max_energy
    
    def can_do(self, energy_cost):
        return self.energy >= energy_cost

    def consume_energy(self, cost):
        self.energy -= cost
```

A ação na interface `textual` faria:
1. Verifica se tem Energia.
2. Desconta a energia.
3. Chama o `TimeManager.start_action(...)`.
4. Atualiza a UI quando a função retornar, mostrando o log do que aconteceu enquanto o tempo passava.
