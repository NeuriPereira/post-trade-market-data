from __future__ import annotations

import pendulum
import requests

from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator

APP_URL = "http://post-trade-mkt:8000"


def _arquivo_disponivel(data_str: str) -> bool:
    """Consulta a B3 para verificar se o arquivo do pregão já foi publicado.

    A B3 não retorna Content-Length no HEAD, então fazemos um GET com streaming
    e verificamos se os primeiros bytes formam um ZIP válido (assinatura PK).
    """
    from datetime import datetime
    data = datetime.strptime(data_str, "%Y-%m-%d")
    data_yymmdd = data.strftime("%y%m%d")
    url = f"https://www.b3.com.br/pesquisapregao/download?filelist=PR{data_yymmdd}.zip"
    try:
        with requests.get(url, stream=True, timeout=15) as r:
            if r.status_code != 200:
                return False
            cabecalho = b""
            for chunk in r.iter_content(chunk_size=256):
                cabecalho += chunk
                if len(cabecalho) >= 2:
                    break
            # Assinatura ZIP: PK\x03\x04
            return cabecalho[:2] == b"PK"
    except Exception:
        return False


def _executar_pipeline(data_str: str) -> dict:
    """Chama o endpoint POST /pipeline/run do post-trade-mkt e aguarda o resultado."""
    r = requests.post(
        f"{APP_URL}/pipeline/run",
        params={"data": data_str},
        timeout=300,
    )
    r.raise_for_status()
    resultado = r.json()
    print(f"Pipeline concluído: {resultado}")
    return resultado


with DAG(
    dag_id="ingestao_bvbg086",
    schedule="30 21 * * 1-5",  # 18h30 Brasília = 21h30 UTC (sem horário de verão desde 2019)
    start_date=pendulum.datetime(2026, 1, 1, tz="America/Sao_Paulo"),
    catchup=False,
    tags=["ingestao", "bvbg086"],
) as dag:

    verificar = ShortCircuitOperator(
        task_id="verificar_arquivo_disponivel",
        python_callable=_arquivo_disponivel,
        op_kwargs={"data_str": "{{ ds }}"},
    )

    pipeline = PythonOperator(
        task_id="executar_pipeline",
        python_callable=_executar_pipeline,
        op_kwargs={"data_str": "{{ ds }}"},
    )

    verificar >> pipeline
