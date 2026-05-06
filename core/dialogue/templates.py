from random import choice
from core.dialogue.intencao import Intencao


TEMPLATES: dict[str, dict[Intencao, list[str]]] = {
    "amigavel": {
        Intencao.CUMPRIMENTAR: [
            "Olá, {alvo}! Bom te ver.",
            "Ei, {alvo}! Tudo bem?",
        ],
        Intencao.ELOGIAR: [
            "{alvo}, você tem um jeito que ilumina o lugar.",
            "Sempre fico feliz de te ver, {alvo}.",
        ],
        Intencao.AMEACAR: [
            "{alvo}, não me obrigue a te machucar.",
        ],
        Intencao.DESPEDIR: [
            "Até mais, {alvo}!", "Cuide-se, {alvo}.",
        ],
    },
    "rabugento": {
        Intencao.CUMPRIMENTAR: [
            "Hm. {alvo}.",
            "Que foi, {alvo}?",
        ],
        Intencao.ELOGIAR: [
            "{alvo}... bom, você não é o pior.",
        ],
        Intencao.AMEACAR: [
            "Some daqui, {alvo}, antes que eu perca a paciência.",
            "{alvo}, não me teste.",
        ],
        Intencao.DESPEDIR: [
            "Vai logo, {alvo}.",
        ],
    },
    "devoto": {
        Intencao.CUMPRIMENTAR: [
            "Que os deuses te abençoem, {alvo}.",
        ],
        Intencao.ELOGIAR: [
            "Vejo a luz neles em você, {alvo}.",
        ],
        Intencao.AMEACAR: [
            "Os deuses julgam, {alvo} — não sou eu.",
        ],
        Intencao.DESPEDIR: [
            "Que sua estrada seja gentil, {alvo}.",
        ],
    },
    "neutro": {
        Intencao.CUMPRIMENTAR: ["Olá, {alvo}."],
        Intencao.ELOGIAR:      ["{alvo}, bom trabalho."],
        Intencao.AMEACAR:      ["Cuidado com o que faz, {alvo}."],
        Intencao.DESPEDIR:     ["Adeus, {alvo}."],
    },
}


def gerar_fala(arquetipo: str, intencao: Intencao, alvo_nome: str = "") -> str:
    bloco = TEMPLATES.get(arquetipo) or TEMPLATES["neutro"]
    variantes = bloco.get(intencao)
    if not variantes:
        return f"...{alvo_nome}."
    return choice(variantes).format(alvo=alvo_nome or "amigo")
