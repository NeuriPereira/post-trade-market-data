
import os
import zipfile
from datetime import datetime


"""Função para extrair conteúdo do arquivo .zip
   Parâmetros:
        caminho_zip:caminho para o arquivo baixado.
        pasta_destino_base: onde salvar o arquivo extraído.
        data_str: data que será usada para organizar a pasta de saída
"""
def extrair_conteudo_zip(caminho_zip, pasta_destino_base="./extraidos", data_str="2025-06-30"):
    
    #se o arquivo .zip não existir, aborta e exibe erro
    if not os.path.exists(caminho_zip):
        print(f"❌ Arquivo ZIP não encontrado: {caminho_zip}")
        return

    # converte data_str em datetime
    data = datetime.strptime(data_str, "%Y-%m-%d")
    # cria uma pasta com a data formatada
    pasta_destino = os.path.join(pasta_destino_base, data.strftime("%Y-%m-%d"))
    # garente que a pasta exista
    os.makedirs(pasta_destino, exist_ok=True)

    # 1. Extrair o primeiro nível (pesquisa-pregao.zip)
    with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
        zip_ref.extractall(pasta_destino)
    print(f"✅ Primeiro nível extraído em: {pasta_destino}")

    # 2. Procurar por .zip internos e extrair
    # Faz um loop sobre os arquivos extraídos no primeiro nível
    # Se encontrar outro arquivo .zip abre e extrai em outra subpasta com o mesmo nome do arquivo(sem .zip)
    # Por fim, finaliza com o arquvo .xml dentro da subpasta
    for item in os.listdir(pasta_destino):
        if item.lower().endswith(".zip"):
            zip_interno_path = os.path.join(pasta_destino, item)
            pasta_extracao = os.path.join(pasta_destino, os.path.splitext(item)[0])
            os.makedirs(pasta_extracao, exist_ok=True)
            with zipfile.ZipFile(zip_interno_path, 'r') as zip_interno:
                zip_interno.extractall(pasta_extracao)
            print(f"✅ Segundo nível extraído em: {pasta_extracao}")

    print("✅ Extração dupla finalizada.")

# Exemplo de uso
extrair_conteudo_zip("./downloads/pesquisa-pregao.zip", data_str="2025-06-30")
