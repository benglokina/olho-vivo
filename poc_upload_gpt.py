import openai
import json

# Função para carregar a chave da API de um arquivo
def carregar_chave(api_key_file):
    try:
        with open(api_key_file, "r", encoding="utf-8") as arquivo:
            return arquivo.read().strip()  # Remove espaços em branco ou quebras de linha extras
    except FileNotFoundError:
        print(f"Erro: O arquivo '{api_key_file}' não foi encontrado.")
        exit(1)
    except Exception as e:
        print(f"Erro ao carregar a chave da API: {e}")
        exit(1)

# Configurar a chave da API
api_key_file = "openai.api_key"  # Arquivo contendo a chave da API
openai.api_key = carregar_chave(api_key_file)

# Função para carregar e enviar o JSON para a API do ChatGPT
def enviar_json_para_chatgpt(arquivo_json):
    try:
        # Carregar o arquivo JSON
        with open(arquivo_json, "r", encoding="utf-8") as arquivo:
            dados_json = json.load(arquivo)

        # Formatar a mensagem para a API do ChatGPT
        mensagem = [
            {"role": "system", "content": "Você é um assistente que analisa dados JSON e fornece insights."},
            {"role": "user", "content": f"Você é um assistente que analisa dados públicos em JSON para identificar possíveis anomalias, fraudes ou indícios de uso irregular de recursos públicos. "
                        "Para cada dado fornecido, realize uma análise detalhada e forneça insights específicos sobre os seguintes aspectos:\n"
                        "1. Discrepâncias em valores, como gastos anormalmente altos em relação à média ou ao contexto.\n"
                        "2. Justificativas inconsistentes, incompletas ou suspeitas para viagens ou eventos registrados.\n"
                        "3. Padrões atípicos de comportamento, como frequência elevada de viagens para um mesmo destino ou por um mesmo beneficiário.\n"
                        "4. Inconsistências entre cargos, funções e motivos apresentados para as viagens.\n"
                        "5. Conflitos de interesse ou relações suspeitas entre beneficiários e órgãos envolvidos.\n"
                        f"Aqui estão os dados: {json.dumps(dados_json, indent=2)}"}
        ]

        # Enviar o JSON para a API
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Alterar para "gpt-4" se preferir
            messages=mensagem,
            max_tokens=1000  # Limitar a quantidade de tokens na resposta
        )

        # Retornar a resposta da API
        print("Resultado da análise:")
        print(resposta.choices[0].message["content"])

    except FileNotFoundError:
        print(f"Erro: O arquivo '{arquivo_json}' não foi encontrado.")
    except json.JSONDecodeError:
        print(f"Erro: O arquivo '{arquivo_json}' não é um JSON válido.")
    except openai.error.OpenAIError as e:
        print(f"Erro na chamada da API: {e}")
    except Exception as e:
        print(f"Erro inesperado: {e}")

# Executar o envio de um arquivo JSON
arquivo_para_enviar = "poc.json"
enviar_json_para_chatgpt(arquivo_para_enviar)
