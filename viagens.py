import requests
import json
import os
from datetime import datetime, timedelta

class ViagensDownloader:
    BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados/viagens"
    CODIGO_ORGAO = "26000"  # Código do órgão hardcoded por enquanto

    def __init__(self, chave_api, output_dir="downloads"):
        self.chave_api = chave_api
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def salvar_em_json(self, dados, nome_arquivo):
        caminho_arquivo = os.path.join(self.output_dir, nome_arquivo)
        with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, indent=4, ensure_ascii=False)
        print(f"Arquivo salvo: {caminho_arquivo}")

    def consultar_viagens(self, data_retorno, pagina=1):
        """
        Consulta viagens a serviço no Portal da Transparência.
        Parâmetros:
            - data_retorno: Data de retorno específica (YYYY-MM-DD).
            - pagina: Página consultada (inteiro).
        """
        # Converter formato de data para DD/MM/AAAA
        data_retorno_formatada = datetime.strptime(data_retorno, "%Y-%m-%d").strftime("%d/%m/%Y")
        data_ida = (datetime.strptime(data_retorno, "%Y-%m-%d") - timedelta(days=30)).strftime("%d/%m/%Y")

        headers = {"chave-api-dados": self.chave_api}
        params = {
            "dataIdaDe": data_ida,
            "dataIdaAte": data_retorno_formatada,
            "dataRetornoDe": data_retorno_formatada,
            "dataRetornoAte": data_retorno_formatada,
            "codigoOrgao": self.CODIGO_ORGAO,
            "pagina": pagina
        }

        response = requests.get(self.BASE_URL, headers=headers, params=params)
        if response.status_code == 200:
            dados = response.json()
            nome_arquivo = f"viagens_{self.CODIGO_ORGAO}_{data_retorno}_pag{pagina}.json"
            self.salvar_em_json(dados, nome_arquivo)
            return dados
        else:
            print(f"Erro: {response.status_code} - {response.text}")
            return None
