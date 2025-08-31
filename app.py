import os
import pandas as pd
from flask import Flask, request, render_template
from fuzzywuzzy import process

PASTA_DADOS = r"C:\projetoIA\dados"
ARQ_DIARIAS = "DIARIASTAXAS.XLS"
ARQ_PROCS = "PROCEDIMENTOS.XLS"

# Lista fixa de convênios
CONVENIOS = ["IMAS", "IPASGO", "UNIMED"]

COLS_DIARIAS = ['CODIGO', 'SERVICO', 'UNIDADE', 'VALOR UNITARIO', 'DATA VIGENCIA', 'CONVENIO']
COLS_PROCS = ['CODIGO PROCEDIMENTO', 'DESCRICAO', 'VALOR UNIT. PROCEDIMENTO', 'CONVENIO']

app = Flask(__name__)

def carregar_dados(nome_arquivo):
    caminho = os.path.join(PASTA_DADOS, nome_arquivo)
    if not os.path.isfile(caminho):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    df = pd.read_excel(caminho)
    df.columns = [col.strip().upper() for col in df.columns]
    return df

df_diarias = carregar_dados(ARQ_DIARIAS)
df_procs = carregar_dados(ARQ_PROCS)

@app.route("/", methods=["GET", "POST"])
def index():
    resposta = ""
    colunas = []
    convenio_selecionado = request.form.get("convenio") if request.method == "POST" else ""
    if request.method == "POST":
        fonte = request.form.get("fonte", "diariastaxas")
        pergunta = request.form.get("pergunta", "").strip()
        if fonte == "procedimentos":
            df = df_procs
            campo_busca = "DESCRICAO"
            colunas = [col for col in COLS_PROCS if col in df.columns]
        else:
            df = df_diarias
            campo_busca = "SERVICO"
            colunas = [col for col in COLS_DIARIAS if col in df.columns]

        # Filtra pelo convênio selecionado, se houver e se a coluna existir
        if convenio_selecionado and 'CONVENIO' in df.columns:
            df = df[df['CONVENIO'].str.upper() == convenio_selecionado.upper()]

        if pergunta and campo_busca in df.columns:
            melhores = process.extract(pergunta, df[campo_busca], limit=len(df))
            linhas_encontradas = []
            for match, score, _ in melhores:
                if score > 60:
                    linha = df[df[campo_busca] == match].iloc[0]
                    linhas_encontradas.append({col: linha.get(col, '') for col in colunas})
            resposta = linhas_encontradas if linhas_encontradas else "Nenhuma informação relevante encontrada."
        else:
            resposta = "Nenhuma informação relevante encontrada."
    return render_template(
        "index.html",
        resposta=resposta,
        colunas=colunas,
        convenios=CONVENIOS,
        convenio_selecionado=convenio_selecionado
    )

if __name__ == "__main__":
    app.run(debug=True)
