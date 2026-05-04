import os
from datetime import datetime
from enum import Enum

import requests

from src.logger import get_logger

_log = get_logger(__name__)


class ExchangeFileType(str, Enum):
    BVBG086 = "PR"   # Boletim de Negociação
    BVBG087 = "IR"   # Arquivo de Índices
    BVBG028 = "IN"   # Cadastro de Instrumentos
    BVBG029 = "II"   # Cadastro de Instrumentos Indicadores
    BVBG186 = "SPRE" # Boletim Simplificado Ações
    BVBG187 = "SPRD" # Boletim Simplificado Derivativos


class ExchangeFileDownloader:
    def __init__(self, pasta_destino: str, tipo: ExchangeFileType = ExchangeFileType.BVBG086) -> None:
        self._pasta_destino = pasta_destino
        self._tipo = tipo

    def download(self, date_str: str) -> str | None:
        data = datetime.strptime(date_str, "%Y-%m-%d")
        data_yymmdd = data.strftime("%y%m%d")
        filename = f"{self._tipo.value}{data_yymmdd}.zip"
        url = f"https://www.b3.com.br/pesquisapregao/download?filelist={filename}"

        _log.info("download_started", filename=filename, date=date_str)
        try:
            with requests.get(url, stream=True, timeout=(10, 120)) as response:
                if response.status_code != 200:
                    _log.error("download_failed", http_status=response.status_code,
                               filename=filename, date=date_str)
                    return None

                dest_filename = "pesquisa-pregao.zip"
                if "Content-Disposition" in response.headers:
                    dispo = response.headers["Content-Disposition"]
                    if "filename=" in dispo:
                        dest_filename = dispo.split("filename=")[-1].strip('"')

                os.makedirs(self._pasta_destino, exist_ok=True)
                caminho = os.path.join(self._pasta_destino, dest_filename)

                with open(caminho, "wb") as f:
                    for chunk in response.iter_content(chunk_size=65536):
                        f.write(chunk)

        except requests.RequestException as e:
            _log.error("download_connection_error", error=str(e), filename=filename, date=date_str)
            return None

        _log.info("download_complete", path=caminho, date=date_str)
        return caminho
