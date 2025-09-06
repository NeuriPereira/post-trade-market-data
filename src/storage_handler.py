import os
import json
import pandas as pd
from typing import List, Dict

from src.config import SRC_PATH, SRC_DOWNLOADS, SRC_EXTRAIDOS

class StorageHandler:
    def __init__(self, dados: List[Dict]):
        self.dados = dados

    def salvar_json(self, caminho: str):
        """Salva os dados como JSON em arquivo"""
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(self.dados, f, indent=4, ensure_ascii=False)
        print(f"✅ JSON salvo em: {caminho}")

    def salvar_parquet(self, caminho: str):
        """Salva os dados em formato Parquet (para Spark ou Pandas)"""
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        df = pd.DataFrame(self.dados)

        # tentativa de converter colunas numéricas (se possível)
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="ignore")

        df.to_parquet(caminho, index=False)
        print(f"✅ Parquet salvo em: {caminho}")

    def buscar_ativo(self, ticker: str) -> List[Dict]:
        """Busca registros de um ativo pelo ticker"""
        return [item for item in self.dados if item.get("ticker") == ticker]
