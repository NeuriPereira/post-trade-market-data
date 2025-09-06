from fastapi import FastAPI
from storage_handler import StorageHandler

# Aqui vamos simular que os dados já foram parseados pelo parse_bvbg086_dinamico2
# Em produção, você chamaria o parse antes e injetaria aqui
from parse_bvbg086_dinamico2 import parse_diretorio_bvbg086
from src.config import SRC_EXTRAIDOS

# Pasta onde estão os XMLs
#PASTA_XML = "/data/EstudoPython/download_arquivo/extraidos/2025-06-30/PR250630"
registros = parse_diretorio_bvbg086(SRC_EXTRAIDOS)

# Cria o handler
handler = StorageHandler(registros)

# Salva também em arquivos (JSON + Parquet)
handler.salvar_json("./saida/registros.json")
handler.salvar_parquet("./saida/registros.parquet")

# API
app = FastAPI()

@app.get("/ativos/{ticker}")
def get_ativo(ticker: str):
    resultados = handler.buscar_ativo(ticker)
    if resultados:
        return resultados
    return {"erro": "Ativo não encontrado"}
