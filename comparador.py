# comparador.py

import pandas as pd
import pdfplumber
import json
import re

def normalizar_texto(texto: str) -> str:
    """Remove acentos, espaços duplos e coloca em minúsculo."""
    import unicodedata
    texto = unicodedata.normalize('NFKD', str(texto))
    texto = ''.join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', texto).strip().lower()


def ler_excel_df(df: pd.DataFrame) -> list[dict]:
    """Normaliza um DataFrame e retorna lista de itens."""
    df = df.copy()
    df.columns = [normalizar_texto(c) for c in df.columns]

    mapa_colunas = {
        'codigo':      ['codigo', 'cod', 'id', 'item'],
        'descricao':   ['descricao', 'descr', 'produto', 'servico', 'nome'],
        'quantidade':  ['quantidade', 'qtd', 'qtde', 'qty'],
        'preco_unit':  ['preco unitario', 'preco_unit', 'valor unit', 'unit price'],
    }

    renomear = {}
    for coluna_padrao, possiveis in mapa_colunas.items():
        for col in df.columns:
            if any(p in col for p in possiveis):
                renomear[col] = coluna_padrao
                break

    df = df.rename(columns=renomear)

    for col in ['descricao', 'quantidade', 'preco_unit']:
        if col not in df.columns:
            raise ValueError(f"Coluna obrigatória '{col}' não encontrada. "
                             f"Colunas disponíveis: {list(df.columns)}")

    if 'codigo' not in df.columns:
        df['codigo'] = [f"ITEM-{i+1:03d}" for i in range(len(df))]

    for col in ['quantidade', 'preco_unit']:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(r'[R$\s]', '', regex=True)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .pipe(pd.to_numeric, errors='coerce')
        )

    return df[['codigo', 'descricao', 'quantidade', 'preco_unit']].to_dict('records')


def ler_excel(caminho: str) -> list[dict]:
    """Lê um arquivo Excel ou CSV e retorna lista de dicionários."""
    df = pd.read_excel(caminho)
    return ler_excel_df(df)


def ler_pdf(caminho: str) -> list[dict]:
    """Extrai tabela de um PDF usando pdfplumber."""
    itens = []

    with pdfplumber.open(caminho) as pdf:
        for pagina in pdf.pages:
            tabelas = pagina.extract_tables()
            for tabela in tabelas:
                if not tabela or len(tabela) < 2:
                    continue

                cabecalho = [normalizar_texto(str(c)) for c in tabela[0]]

                for linha in tabela[1:]:
                    if not any(linha):
                        continue
                    item = dict(zip(cabecalho, linha))
                    itens.append(item)

    if not itens:
        raise ValueError("Nenhuma tabela encontrada no PDF. "
                         "Verifique se o arquivo tem tabelas estruturadas.")

    df = pd.DataFrame(itens)
    return ler_excel_df(df)


def ler_arquivo(caminho: str) -> list[dict]:
    """Detecta o tipo do arquivo e chama o leitor correto."""
    caminho = caminho.lower()
    if caminho.endswith(('.xlsx', '.xls')):
        return ler_excel(caminho)
    elif caminho.endswith('.csv'):
        df = pd.read_csv(caminho)
        return ler_excel_df(df)
    elif caminho.endswith('.pdf'):
        return ler_pdf(caminho)
    else:
        raise ValueError(f"Formato não suportado: {caminho}. "
                         "Use Excel (.xlsx), CSV ou PDF.")


def montar_payload(caminho_fornecedor: str, 
                   caminho_interno: str,
                   nome_fornecedor: str = "Fornecedor") -> dict:
    """
    Lê os dois arquivos e monta o dicionário JSON
    que será enviado ao agente.
    """
    itens_forn = ler_arquivo(caminho_fornecedor)
    itens_int  = ler_arquivo(caminho_interno)
    
    return {
        "fornecedor": {
            "nome": nome_fornecedor,
            "itens": itens_forn
        },
        "interno": {
            "itens": itens_int
        }
    }