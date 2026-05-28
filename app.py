# app.py

import os
import gradio as gr
from comparador import montar_payload
from agent import analisar, perguntar

# Estado global da sessão (histórico do chat)
historico_global = []


def processar_orcamentos(arquivo_fornecedor, arquivo_interno, nome_fornecedor):
    """Chamado quando o usuário clica em 'Analisar'."""
    global historico_global
    
    if arquivo_fornecedor is None or arquivo_interno is None:
        return " Por favor, envie os dois arquivos antes de analisar.", []
    
    try:
        payload = montar_payload(
            caminho_fornecedor=arquivo_fornecedor.name,
            caminho_interno=arquivo_interno.name,
            nome_fornecedor=nome_fornecedor or "Fornecedor"
        )
        
        resultado, historico_global = analisar(payload)
        
        # Retorna análise + limpa o chat
        return resultado, []
    
    except Exception as e:
        return f" Erro ao processar arquivos:\n\n{str(e)}", []


def responder_pergunta(mensagem, historico_chat):
    """Chamado quando o usuário envia uma mensagem no chat."""
    global historico_global
    
    if not historico_global:
        return " Faça uma análise primeiro antes de fazer perguntas.", historico_chat
    
    resposta, historico_global = perguntar(historico_global, mensagem)
    
    historico_chat.append((mensagem, resposta))
    return "", historico_chat


# ── Interface Gradio ────────────────────────────────────────────

app = gr.Blocks(title="OrcaAgent — Comparador de Orçamentos")
with app:
    
    gr.Markdown("#  OrcaAgent — Comparador de Orçamentos")
    gr.Markdown("Envie o orçamento do fornecedor e a sua planilha interna. "
                "O agente faz a comparação completa e fica disponível para perguntas.")
    
    # ── Seção de upload ─────────────────────────────────────────
    with gr.Row():
        with gr.Column():
            arquivo_forn = gr.File(
                label=" Orçamento do Fornecedor (Excel ou PDF)",
                file_types=[".xlsx", ".xls", ".pdf", ".csv"]
            )
        with gr.Column():
            arquivo_int = gr.File(
                label=" Planilha Interna (Excel ou CSV)",
                file_types=[".xlsx", ".xls", ".csv"]
            )
    
    nome_forn = gr.Textbox(
        label="Nome do Fornecedor ",
        placeholder="Ex: RPM Haddad Empreendimentos"
    )
    
    btn_analisar = gr.Button(" Analisar Orçamentos", variant="primary", size="lg")
    
    # ── Resultado da análise ────────────────────────────────────
    gr.Markdown("---")
    gr.Markdown("## Resultado da Análise")
    
    resultado = gr.Markdown(value="*Aguardando arquivos...*")
    
    # ── Chat de follow-up ───────────────────────────────────────
    gr.Markdown("---")
    gr.Markdown("##  Perguntas de Follow-up")
    gr.Markdown("Após a análise, faça perguntas como: "
                "*'Qual item tem maior diferença?'*, "
                "*'Escreva um e-mail de negociação'*, "
                "*'E se o fornecedor der 10% de desconto?'*")
    
    chatbot = gr.Chatbot(height=400)
    
    with gr.Row():
        caixa_texto = gr.Textbox(
            placeholder="Digite sua pergunta...",
            show_label=False,
            scale=4
        )
        btn_enviar = gr.Button("Enviar", variant="secondary", scale=1)
    
    # ── Conexão dos eventos ─────────────────────────────────────
    btn_analisar.click(
        fn=processar_orcamentos,
        inputs=[arquivo_forn, arquivo_int, nome_forn],
        outputs=[resultado, chatbot]
    )
    
    btn_enviar.click(
        fn=responder_pergunta,
        inputs=[caixa_texto, chatbot],
        outputs=[caixa_texto, chatbot]
    )
    
    caixa_texto.submit(
        fn=responder_pergunta,
        inputs=[caixa_texto, chatbot],
        outputs=[caixa_texto, chatbot]
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    app.launch(server_name="0.0.0.0", server_port=port, theme=gr.themes.Soft())