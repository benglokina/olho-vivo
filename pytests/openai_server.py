import os
import sys
from openai_server import OpenAI
from flask import Flask, request, jsonify


class OpenAIServer:
    def __init__(self, api_key_path="chatgpt.api_key", model="gpt-4o"):
        # Ler a chave de API do arquivo
        with open(api_key_path, "r") as f:
            self.api_key = f.read().strip()
        self.model = model
        self.client = OpenAI(api_key=self.api_key)  # Nova sintaxe para inicializar o cliente OpenAI
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
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Você é um assistente útil."},
                        {"role": "user", "content": prompt}
                    ]
                )
                generated_text = response.choices[0].message.content.strip()
                return jsonify({"response": generated_text})
            except Exception as e:
                return jsonify({"error": f"Erro ao gerar resposta: {e}"}), 500

    def run(self, host="0.0.0.0", port=5001):
        print(f"[SERVER] Executando servidor OpenAI em http://{host}:{port}")
        self.app.run(host=host, port=port)


def main():
    if len(sys.argv) < 3:
        print("Uso: python openai_server.py server --port <porta>")
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
        server = OpenAIServer(api_key_path="chatgpt.api_key", model="gpt-4o")
        server.run(port=port)
    else:
        print("Modo inválido. Use 'server'.")


if __name__ == "__main__":
    main()