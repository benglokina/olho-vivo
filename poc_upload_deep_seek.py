import json
import requests
import time

class DeepSeekUploader:
    def __init__(self, api_key_file: str, base_url: str = "https://api.deepseek.com/v1"):
        self.api_key = self._load_api_key(api_key_file)
        self.base_url = base_url

    def _load_api_key(self, api_key_file: str) -> str:
        """Carrega a chave da API a partir de um arquivo."""
        try:
            with open(api_key_file, 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo de chave de API não encontrado: {api_key_file}")
        except Exception as e:
            raise Exception(f"Erro ao carregar a chave da API: {e}")

    def _chunk_data(self, data, chunk_size):
        """Divide os dados em partes menores para processar grandes arquivos."""
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]

    def upload_json(self, json_file: str, chunk_size=100):
        """Faz upload do arquivo JSON para a API DeepSeek e retorna a resposta."""
        try:
            with open(json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Verifica se o JSON está no formato correto
            if isinstance(data, list):
                data_chunks = list(self._chunk_data(data, chunk_size))
            elif isinstance(data, dict):
                data_chunks = [data]
            else:
                raise ValueError("O arquivo JSON deve conter um objeto ou uma lista.")

            all_responses = []

            for idx, chunk in enumerate(data_chunks):
                print(f"Processando parte {idx + 1}/{len(data_chunks)}...")

                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                user_message = (
                    "Você é um assistente que analisa dados públicos em JSON para identificar possíveis anomalias, fraudes ou indícios de uso irregular de recursos públicos. "
                    "Para cada dado fornecido, realize uma análise detalhada e forneça insights específicos sobre os seguintes aspectos:\n"
                    "1. Discrepâncias em valores, como gastos anormalmente altos em relação à média ou ao contexto.\n"
                    "2. Justificativas inconsistentes, incompletas ou suspeitas para viagens ou eventos registrados.\n"
                    "3. Padrões atípicos de comportamento, como frequência elevada de viagens para um mesmo destino ou por um mesmo beneficiário.\n"
                    "4. Inconsistências entre cargos, funções e motivos apresentados para as viagens.\n"
                    "5. Conflitos de interesse ou relações suspeitas entre beneficiários e órgãos envolvidos.\n"
                    "Aqui estão os dados analisados:\n"
                    f"{json.dumps(chunk, indent=2)}"
                )
                payload = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "Você é um modelo especializado em encontrar anomalias e irregularidades em dados governamentais."},
                        {"role": "user", "content": user_message}
                    ]
                }

                try:
                    start_time = time.time()
                    response = requests.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=120  # Timeout de 60 segundos
                    )
                    elapsed_time = time.time() - start_time
                    print(f"Parte {idx + 1} processada em {elapsed_time:.2f} segundos.")

                    if response.status_code == 200:
                        all_responses.append(response.json()["choices"][0]["message"]["content"])
                    else:
                        raise Exception(f"Erro na API: {response.status_code} - {response.text}")

                except requests.exceptions.Timeout:
                    print(f"Timeout na parte {idx + 1}. Tentando novamente...")
                    continue  # Ou implemente um sistema de retry com backoff
                except Exception as e:
                    print(f"Erro ao processar a parte {idx + 1}: {e}")
                    continue

            return all_responses

        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo JSON não encontrado: {json_file}")
        except ValueError as ve:
            raise ValueError(f"Erro no formato do JSON: {ve}")
        except Exception as e:
            raise Exception(f"Erro ao processar o arquivo ou enviar para a API: {e}")

if __name__ == "__main__":
    # Configurações iniciais
    api_key_file = "deepseek.api_key"
    json_file = "poc.json"

    # Cria a instância da classe e envia os dados
    uploader = DeepSeekUploader(api_key_file)
    try:
        resultados = uploader.upload_json(json_file)
        print("Resultados da análise:")
        for resultado in resultados:
            print(resultado)
    except Exception as e:
        print(e)
