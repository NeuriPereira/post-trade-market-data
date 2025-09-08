
import os
import xml.etree.ElementTree as ET
from datetime import datetime

from src.config import SRC_EXTRAIDOS

# Namespace ISO e BVMF
# define o namespace XML que o ElementTree precisa para localizar os elementos. 
# No caso, "urn:bvmf.217.01.xsd
NS_BVMF = {
    'bvmf': 'urn:bvmf.217.01.xsd',
}

""" Função converte tags em snake_case
    Exemplo: FinInstrmQty → fin_instrm_qty
"""
def to_snake_case(text):
    return ''.join(['_' + c.lower() if c.isupper() else c for c in text]).lstrip('_')

""" Função de leitura do arquivo XML"""
def parse_bvbg086_xml(caminho_xml):
    # ET.iterparse: faz o parsing streaming do XML → ótimo para arquivos grandes
    # events=("end",): dispara um evento sempre que fecha uma tag →  no caso, capturar o (PricRpt).
    dados = []
    context = ET.iterparse(caminho_xml, events=("end",))
    
    # A cada elemento fechado, o código verifica se é um bloco <...PricRpt> (Price Report).
    # Cada <PricRpt> corresponde a um registro de preço.
    
    for event, elem in context:
        if elem.tag.endswith("PricRpt"):
            try:
                
                """ 
                    Função auxiliar que simplifica a busca de valores dentro do elem usando XPaths curtos.
                    Se o campo não existir → retorna None (porque o schema é flexível e pode omitir).
                """
                def text(xpath):
                    el = elem.find(xpath, NS_BVMF)
                    return el.text if el is not None else None

                # Cria o dicionário base com os campos principais e fixos
                registro = {
                    "ticker": text("bvmf:SctyId/bvmf:TckrSymb"),
                    "data": text("bvmf:TradDt/bvmf:Dt"),
                    "codigo": text("bvmf:FinInstrmId/bvmf:OthrId/bvmf:Id"),
                    "trad_qty": text("bvmf:TradDtls/bvmf:TradQty"),
                    
                }

                # A tag <FinInstrmAttrbts> contém muitos campos opcionais (preço, volume, bid, ask etc).
                # Esse loop percorre cada filho e:
                # Converte o nome da tag para snake_case.
                # Salva o valor como registro[tag] = valor.
                # Se houver atributos XML (attr), também salva, adicionando sufixo.
                fin_attr = elem.find("bvmf:FinInstrmAttrbts", NS_BVMF)
                if fin_attr is not None:
                    for child in fin_attr:
                        tag_base = to_snake_case(child.tag.split("}")[-1])
                        registro[tag_base] = child.text
                        for attr_k, attr_v in child.attrib.items():
                            registro[f"{tag_base}_{attr_k.lower()}"] = attr_v
                            
                # Cada registro é salvo na lista dados.
                # elem.clear(): limpa o nó da memória → essencial para arquivos grandes (não sobrecarregar RAM).
                dados.append(registro)
            except Exception as e:
                print(f"❌ Erro ao processar registro: {e}")

            elem.clear()

    return dados

""" 
    Varre a pasta, pega todos os .xml e aplica parse_bvbg086_xml.
    Junta tudo em uma única lista (todos_dados).
"""
def parse_diretorio_bvbg086(pasta):
    todos_dados = []
    for root, _, files in os.walk(pasta):
        for nome_arquivo in files:
            if nome_arquivo.endswith(".xml"):
                caminho = os.path.join(root, nome_arquivo)
                print(f"📄 Processando: {caminho}")
                dados = parse_bvbg086_xml(caminho)
                todos_dados.extend(dados)
    return todos_dados

