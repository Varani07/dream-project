from random import randint as ri


def probabilidade(porcentagem:int, fadiga:bool, **kwargs) -> bool:
    num_aleatorio = ri(1, 1000)
    porcentagem *= 10 
    #* Iterando pelos key word arguments, que estão estruturados como por exemplo: 
    #* sorte=(5, self.sorte, True) | true significa que o valor vai somar e aumentar
    #* a chance de dar certo, se for false vai diminuir. 5 vai ser o valor multiplicado
    #* pela sorte e depois o resultado será somado a porcentagem

    #* Se fadiga for True os bonus de acerto são zerados e para cada kwarg com False é subtraído 5% de chance

    for value in kwargs.values():
        if value[2]:
            if not fadiga:
                porcentagem += value[0] * value[1]
        else:
            porcentagem -= value[0] * value[1] 
            if fadiga:
                porcentagem -= 50

    #* Verifica se o número aleatório é menor que o resultado da porcentagem
    #* Dependendo retorna True ou False
    if porcentagem >= num_aleatorio:
        return True
    else:
        return False
        