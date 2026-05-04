import os
from dotenv import load_dotenv

load_dotenv()

def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Variável de ambiente obrigatória não definida: {name}")
    return value

SRC_DOWNLOADS = _require("SRC_DOWNLOADS")
SRC_EXTRAIDOS = _require("SRC_EXTRAIDOS")
