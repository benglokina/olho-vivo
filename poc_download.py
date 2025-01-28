import requests
import json

# Configuração inicial
BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"
TOKEN = "37c8c28db463b37268da42ef608a4055"  # Substitua pelo seu token de API


def salvar_em_json(dados, nome_arquivo):
    with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)

def consultar_viagens(data_ida_de, data_ida_ate, data_retorno_de, data_retorno_ate, codigo_orgao, pagina=1):
    """
    Consulta viagens a serviço no Portal da Transparência.
    Parâmetros obrigatórios:
        - data_ida_de: Data de ida a partir de (DD/MM/AAAA).
        - data_ida_ate: Data de ida até (DD/MM/AAAA).
        - data_retorno_de: Data de retorno a partir de (DD/MM/AAAA).
        - data_retorno_ate: Data de retorno até (DD/MM/AAAA).
        - codigo_orgao: Código do órgão (SIAFI).
        - pagina: Página consultada (inteiro).
    """
    endpoint = f"{BASE_URL}/viagens"
    headers = {"chave-api-dados": TOKEN}
    params = {
        "dataIdaDe": data_ida_de,
        "dataIdaAte": data_ida_ate,
        "dataRetornoDe": data_retorno_de,
        "dataRetornoAte": data_retorno_ate,
        "codigoOrgao": codigo_orgao,
        "pagina": pagina
    }

    response = requests.get(endpoint, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro: {response.status_code} - {response.text}")
        return None

# Teste da função
resultado = consultar_viagens(
    data_ida_de="01/01/2023",       # Data de ida inicial
    data_ida_ate="31/01/2023",      # Data de ida final
    data_retorno_de="01/01/2023",   # Data de retorno inicial
    data_retorno_ate="31/01/2023",  # Data de retorno final
    codigo_orgao="26000",           # Código do órgão (exemplo: Ministério da Saúde)
    pagina=1                        # Página inicial
)

# Imprime o resultado
if resultado:
    salvar_em_json(resultado, 'poc.json')