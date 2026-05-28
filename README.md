# OrcaAgent — Comparador de Orçamentos

## Como rodar

1. Ative o ambiente virtual:
```bat
venv\Scripts\activate
```

2. Instale as dependências:
```bat
pip install -r requirements.txt
```

3. Defina a chave Anthropic na mesma janela:
```bat
set ANTHROPIC_API_KEY=sk-<sua_chave>
```

4. Execute a aplicação:
```bat
python app.py
```

5. Abra o link do Gradio que aparecer no terminal.

## Observações
- Os arquivos `agent.py` e `prompt.py` foram movidos para a raiz do projeto para que `app.py` importe corretamente.
- Se preferir, use Excel (`.xlsx`) ou CSV para os dados internos; para o fornecedor, também é possível enviar PDF.

## Deploy no Render
1. Faça commit deste projeto no GitHub.
2. No Render, crie um novo `Web Service` e conecte ao repositório.
3. Configure o ambiente Python:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
4. Adicione a variável de ambiente `ANTHROPIC_API_KEY` no painel do Render.
5. O serviço deve iniciar automaticamente e usar a porta fornecida pelo Render.

### Observação importante
- O `app.py` já está configurado para usar `PORT` do ambiente e `server_name="0.0.0.0"`.
- Se você quiser um domínio próprio, configure o domínio customizado no painel do Render após o deploy.
