# agent.py

import anthropic
import json
from prompt import SYSTEM_PROMPT

client = anthropic.Anthropic()


def analisar(payload: dict) -> tuple[str, list]:
    """
    Envia os dados para o agente e retorna:
    - resposta (str): análise completa em Markdown
    - historico (list): histórico para usar no chat de follow-up
    """
    mensagem = (
        "Por favor, realize a análise completa dos orçamentos abaixo.\n\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
    )

    historico = [{"role": "user", "content": mensagem}]

    resposta = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=historico
    )

    texto = resposta.content[0].text
    historico.append({"role": "assistant", "content": texto})

    return texto, historico


def perguntar(historico: list, pergunta: str) -> tuple[str, list]:
    """
    Envia uma pergunta de follow-up mantendo o contexto da análise.
    Retorna a resposta e o histórico atualizado.
    """
    historico.append({"role": "user", "content": pergunta})

    resposta = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=historico
    )

    texto = resposta.content[0].text
    historico.append({"role": "assistant", "content": texto})

    return texto, historico
