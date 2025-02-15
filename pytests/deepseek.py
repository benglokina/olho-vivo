import os
import sys
import requests
from flask import Flask, request, jsonify


class DeepSeekServer:
    def __init__(self, api_key_path="deepseek.api_key", model="deepseek-r1"):
        # Ler a chave de API do arquivo
        with open(api_key_path, "r") as f:
            self.api_key = f.read().strip()
        self.model = model
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route("/generate", methods=["POST"])
        def generate():
            data = request.get_json()
            if not data or "prompt" not in data:
                return jsonify({"error": "Prompt não informado."}), 400
            prompt = data["prompt"]
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "Você é um assistente útil."},
                        {"role": "user", "content": prompt}
                    ]
                }
                response = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=payload)
                response.raise_for_status()
                response_data = response.json()
                generated_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
                return jsonify({"response": generated_text})
            except Exception as e:
                return jsonify({"error": f"Erro ao gerar resposta: {e}"}), 500

    def run(self, host="0.0.0.0", port=5000):
        print(f"[SERVER] Executando servidor DeepSeek em http://{host}:{port}")
        self.app.run(host=host, port=port)


def main():
    if len(sys.argv) < 3:
        print("Uso: python deepseek.py server --port <porta>")
        sys.exit(1)
    mode = sys.argv[1].lower()
    if mode == "server":
        try:
            # Verifica se o argumento é --port <valor>
            if sys.argv[2] == "--port":
                port = int(sys.argv[3])
            else:
                port = int(sys.argv[2])  # Assume que o valor da porta é direto
        except (ValueError, IndexError):
            print("Porta inválida. Use um número inteiro.")
            sys.exit(1)
        server = DeepSeekServer(api_key_path="deepseek.api_key", model="deepseek-r1")
        server.run(port=port)
    else:
        print("Modo inválido. Use 'server'.")


if __name__ == "__main__":
    main()