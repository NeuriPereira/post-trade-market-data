import os #manipulação de diretórios e caminhos de arquivos
import requests #biblioteca HTTP usada para baixar arquivos
from datetime import datetime #manipulação de datas

"""Função para baixar arquivos
   Parâmetros:
        data_str:data em formato "YYYY-MM-DD" (ex: "2025-06-30"). Se não passar nada, pega a data de hoje.
        pasta_destino: onde salvar o arquivo (./downloads por padrão). 
"""
def baixar_pregao_zip(data_str=None, pasta_destino="./downloads"):
    if data_str is None:
        data = datetime.today()
    else:
        data = datetime.strptime(data_str, "%Y-%m-%d")

    data_formatada = data.strftime("%y%m%d")
    
    #O nome remoto do arquivo na B3 segue esse padrão de exemplo:PR250630.zip
    nome_arquivo_remoto = f"PR{data_formatada}.zip" 
    
    #monta a url para o arquivo
    url = f"https://www.b3.com.br/pesquisapregao/download?filelist={nome_arquivo_remoto}"

    print(f"🔄 Baixando de: {url}")

    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Erro ao baixar arquivo: status {response.status_code}")
        return

    # Verifica o nome sugerido no Content-Disposition (default: pesquisa-pregao.zip)
    # Normalmente, a B3 retorna o arquivo com nome fixo "pesquisa-pregao.zip".
    # Mas, por segurança, o código verifica o header Content-Disposition e extrai o nome sugerido, se existir.
    filename = "pesquisa-pregao.zip"
    if "Content-Disposition" in response.headers:
        dispo = response.headers["Content-Disposition"]
        if "filename=" in dispo:
            filename = dispo.split("filename=")[-1].strip('"')

    # Cria o diretório e salva o arquivo ZIP
    os.makedirs(pasta_destino, exist_ok=True)
    caminho_arquivo = os.path.join(pasta_destino, filename)

    with open(caminho_arquivo, "wb") as f:
        f.write(response.content)

    print(f"✅ Arquivo salvo em: {caminho_arquivo}")
    return caminho_arquivo

# Exemplo de uso
baixar_pregao_zip("2025-06-30")
