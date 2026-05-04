import os
import zipfile
from datetime import datetime

from src.logger import get_logger

_log = get_logger(__name__)


class ZipExtractor:
    def __init__(self, pasta_destino_base: str) -> None:
        self._pasta_destino_base = pasta_destino_base

    def extract(self, zip_path: str, date_str: str) -> str:
        if not os.path.exists(zip_path):
            raise FileNotFoundError(f"Arquivo ZIP não encontrado: {zip_path}")

        data = datetime.strptime(date_str, "%Y-%m-%d")
        pasta_destino = os.path.join(self._pasta_destino_base, data.strftime("%Y-%m-%d"))
        os.makedirs(pasta_destino, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(pasta_destino)
        _log.info("zip_level1_extracted", path=pasta_destino, date=date_str)

        inner_zips = [i for i in os.listdir(pasta_destino) if i.lower().endswith(".zip")]
        for item in inner_zips:
            zip_interno = os.path.join(pasta_destino, item)
            pasta_interna = os.path.join(pasta_destino, os.path.splitext(item)[0])
            os.makedirs(pasta_interna, exist_ok=True)
            with zipfile.ZipFile(zip_interno, "r") as zf2:
                zf2.extractall(pasta_interna)
            _log.info("zip_level2_extracted", path=pasta_interna, date=date_str)

        _log.info("extraction_complete", date=date_str, inner_zips=len(inner_zips))
        return pasta_destino
