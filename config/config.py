import os
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

# Agora expõe as variáveis
SRC_PATH = os.getenv("SRC_PATH")
SRC_DOWNLOADS = os.getenv("SRC_DOWNLOADS")
SRC_EXTRAIDOS = os.getenv("SRC_EXTRAIDOS")
