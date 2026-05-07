from random import choice
from core.dialogue.intention import Intention


TEMPLATES: dict[str, dict[Intention, list[str]]] = {
    "amigavel": {
        Intention.CUMPRIMENTAR: [
            "Olá, {alvo}! Bom te ver.",
            "Ei, {alvo}! Tudo bem?",
        ],
        Intention.ELOGIAR: [
            "{alvo}, você tem um jeito que ilumina o lugar.",
            "Sempre fico feliz de te ver, {alvo}.",
        ],
        Intention.AMEACAR: [
            "{alvo}, não me obrigue a te machucar.",
        ],
        Intention.DESPEDIR: [
            "Até mais, {alvo}!", "Cuide-se, {alvo}.",
        ],
    },
    "rabugento": {
        Intention.CUMPRIMENTAR: [
            "Hm. {alvo}.",
            "Que foi, {alvo}?",
        ],
        Intention.ELOGIAR: [
            "{alvo}... bom, você não é o pior.",
        ],
        Intention.AMEACAR: [
            "Some daqui, {alvo}, antes que eu perca a paciência.",
            "{alvo}, não me teste.",
        ],
        Intention.DESPEDIR: [
            "Vai logo, {alvo}.",
        ],
    },
    "devoto": {
        Intention.CUMPRIMENTAR: [
            "Que os deuses te abençoem, {alvo}.",
        ],
        Intention.ELOGIAR: [
            "Vejo a luz neles em você, {alvo}.",
        ],
        Intention.AMEACAR: [
            "Os deuses julgam, {alvo} — não sou eu.",
        ],
        Intention.DESPEDIR: [
            "Que sua estrada seja gentil, {alvo}.",
        ],
    },
    "neutro": {
        Intention.CUMPRIMENTAR: ["Olá, {alvo}."],
        Intention.ELOGIAR:      ["{alvo}, bom trabalho."],
        Intention.AMEACAR:      ["Cuidado com o que faz, {alvo}."],
        Intention.DESPEDIR:     ["Adeus, {alvo}."],
    },
}


def generate_speech(archetype: str, intention: Intention, target_name: str = "") -> str:
    block = TEMPLATES.get(archetype) or TEMPLATES["neutro"]
    variants = block.get(intention)
    if not variants:
        return f"...{target_name}."
    return choice(variants).format(alvo=target_name or "amigo")
