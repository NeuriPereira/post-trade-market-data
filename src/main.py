import uvicorn
from src.config import SRC_EXTRAIDOS
from src.parse_bvbg086_dinamico2 import parse_diretorio_bvbg086

if __name__=="__main__":
    uvicorn.run("src.api:app", host='0.0.0.0', port=8000, reload=True)

    registros = parse_diretorio_bvbg086(SRC_EXTRAIDOS)
    print(f"✅ Total de registros extraídos: {len(registros)}")
    for r in registros[:5]:
        print(r)

