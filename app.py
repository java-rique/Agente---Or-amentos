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

    import tempfile
    import traceback

    def _ensure_path(uploaded):
        """Retorna um filesystem path válido para o arquivo enviado pelo Gradio."""
        if uploaded is None:
            return None

        # Se for uma string path existente
        if isinstance(uploaded, str) and os.path.exists(uploaded):
            return uploaded

        # Se o objeto tem atributo .name com caminho
        path = getattr(uploaded, 'name', None)
        if path and os.path.exists(path):
            return path

        # alguns objetos Gradio usam `tmp_path` ou `path`
        candidate_paths = []
        if isinstance(uploaded, dict):
            candidate_paths += [uploaded.get('tmp_path'), uploaded.get('path'), uploaded.get('name')]
        candidate_paths += [getattr(uploaded, 'tmp_path', None), getattr(uploaded, 'path', None)]

        for candidate in candidate_paths:
            if isinstance(candidate, str) and os.path.exists(candidate):
                return candidate

        # Se for um file-like, leia e salve em arquivo temporário
        try:
            data = None
            if hasattr(uploaded, 'read'):
                uploaded.seek(0)
                data = uploaded.read()
            elif isinstance(uploaded, dict) and 'data' in uploaded:
                data = uploaded['data']

            if data is not None:
                suffix = ''
                nameattr = None
                if hasattr(uploaded, 'name'):
                    nameattr = getattr(uploaded, 'name')
                elif isinstance(uploaded, dict):
                    nameattr = uploaded.get('name')
                elif hasattr(uploaded, 'filename'):
                    nameattr = getattr(uploaded, 'filename')

                if nameattr:
                    suffix = os.path.splitext(str(nameattr))[1]

                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                if isinstance(data, str):
                    data = data.encode()
                tmp.write(data)
                tmp.close()
                return tmp.name
        except Exception:
            print("Erro ao criar arquivo temporario para upload:")
            traceback.print_exc()

        return None

    try:
        caminho_forn = _ensure_path(arquivo_fornecedor)
        caminho_int = _ensure_path(arquivo_interno)

        if not caminho_forn or not caminho_int:
            return " Erro ao processar arquivos: não foi possível ler os arquivos enviados.", []

        print(f"DEBUG: caminho_forn={caminho_forn} caminho_int={caminho_int}")

        payload = montar_payload(
            caminho_fornecedor=caminho_forn,
            caminho_interno=caminho_int,
            nome_fornecedor=nome_fornecedor or "Fornecedor"
        )

        resultado, historico_global = analisar(payload)

        # Retorna análise + limpa o chat
        return resultado, []

    except Exception as e:
        import traceback
        traceback.print_exc()
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