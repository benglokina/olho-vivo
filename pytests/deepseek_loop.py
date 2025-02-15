import sys
import os
import time
import shutil
import subprocess
import requests
import re

########################################
# Classe Cliente (Client)
########################################
class DeepSeekClient:
    def __init__(self, server_url="http://localhost:5000", history_dir="history"):
        self.server_url = server_url
        self.history_dir = history_dir
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)

    def ensure_initial_files(self, tetris_path="tetris.py", output_path="output.txt"):
        """Garante que os arquivos tetris.py e output.txt existam. Cria versões iniciais se necessário."""
        if not os.path.exists(tetris_path):
            with open(tetris_path, "w", encoding="utf-8") as f:
                f.write("# Código inicial do Tetris\n")
            print(f"[CLIENT] Arquivo {tetris_path} criado com conteúdo inicial.")
        if not os.path.exists(output_path):
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("Saída inicial do console.\n")
            print(f"[CLIENT] Arquivo {output_path} criado com conteúdo inicial.")

    def read_files(self, tetris_path="tetris.py", output_path="output.txt"):
        """Lê os arquivos tetris.py e output.txt."""
        try:
            with open(tetris_path, "r", encoding="utf-8") as f:
                tetris_code = f.read().strip()
            with open(output_path, "r", encoding="utf-8") as f:
                output_console = f.read().strip()
            return tetris_code, output_console
        except Exception as e:
            print(f"[CLIENT] Erro ao ler arquivos: {e}")
            return None, None

    def create_prompt(self, tetris_code, output_console):
        """Cria o arquivo prompt.txt com base no código e na saída do console."""
        prompt_content = (
            "Corrigir os erros de lógica e compilação no código abaixo:\n"
            f"{tetris_code}\n\n"
            "A saída do console na execução do código foi:\n"
            f"{output_console}\n\n"
            "Além de corrigir os erros, crie um conjunto de testes automatizados que verifiquem as seguintes funcionalidades principais do Tetris:\n"
            "1. Peças devem cair automaticamente.\n"
            "2. O jogador deve poder mover as peças para a esquerda, direita e rotacioná-las.\n"
            "3. Quando uma linha for preenchida, ela deve ser removida e o jogador deve ganhar pontos.\n"
            "4. O jogo deve terminar quando as peças atingirem o topo da tela.\n"
            "5. O placar deve ser atualizado corretamente.\n"
            "6. O jogo deve rodar sem erros ou travamentos.\n\n"
            "Inclua os testes no final do código e adicione comentários explicativos sobre como executá-los.\n"
            "Se o código já estiver correto e os testes passarem, indique isso explicitamente no início do arquivo."
        )
        with open("prompt.txt", "w", encoding="utf-8") as f:
            f.write(prompt_content)
        print("[CLIENT] Arquivo prompt.txt criado com sucesso.")

    def move_to_history(self, tetris_path="tetris.py", output_path="output.txt"):
        """Move os arquivos tetris.py e output.txt para a pasta history com numeração incremental."""
        files = os.listdir(self.history_dir)
        tetris_count = len([f for f in files if f.startswith("tetris_")])
        new_tetris_name = f"tetris_{tetris_count + 1:03d}.py"
        new_output_name = f"output_{tetris_count + 1:03d}.txt"
        shutil.move(tetris_path, os.path.join(self.history_dir, new_tetris_name))
        shutil.move(output_path, os.path.join(self.history_dir, new_output_name))
        print(f"[CLIENT] Arquivos movidos para history: {new_tetris_name}, {new_output_name}")

    def send_prompt(self):
        """Envia o arquivo prompt.txt para o servidor e retorna a resposta."""
        try:
            with open("prompt.txt", "r", encoding="utf-8") as f:
                prompt = f.read().strip()
            payload = {"prompt": prompt}
            response = requests.post(f"{self.server_url}/generate", json=payload)
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                print(f"[CLIENT] Erro no servidor: {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"[CLIENT] Exceção na requisição ao servidor: {e}")
            return None

    def extract_python_code(self, response):
        """
        Extrai apenas o primeiro bloco de código Python da resposta do servidor.
        Assume que o código está entre ```python e ```.
        """
        code_pattern = r"```python(.*?)```"
        matches = re.findall(code_pattern, response, re.DOTALL)
        if matches:
            # Retorna apenas o primeiro bloco de código encontrado
            return matches[0].strip()
        else:
            print("[CLIENT] Não foi possível encontrar código Python na resposta. Resposta completa:")
            print(response)  # Imprime a resposta completa para depuração
            return None

    def update_tetris_code(self, python_code):
        """Atualiza o arquivo tetris.py com o código gerado pelo servidor."""
        with open("tetris.py", "w", encoding="utf-8") as f:
            f.write(python_code)
        print("[CLIENT] Arquivo tetris.py atualizado com sucesso.")

    def execute_tetris(self):
        """Executa o arquivo tetris.py com um timeout e salva a saída em output.txt."""
        try:
            # Define um timeout de 30 segundos (ajuste conforme necessário)
            TIMEOUT_SECONDS = 30
            result = subprocess.run(
                ["python", "tetris.py"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=TIMEOUT_SECONDS  # Adiciona timeout
            )
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write(result.stdout)
            print("[CLIENT] Execução do tetris.py concluída. Saída salva em output.txt.")
        except subprocess.TimeoutExpired:
            error_message = f"[CLIENT] Erro: O script tetris.py excedeu o tempo limite de {TIMEOUT_SECONDS} segundos."
            print(error_message)
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write(error_message + "\n")
        except Exception as e:
            print(f"[CLIENT] Erro ao executar tetris.py: {e}")
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write(f"Erro ao executar o código: {e}\n")

    def run_iteration(self):
        """Executa uma iteração completa do processo."""
        # Passo 1: Ler arquivos tetris.py e output.txt
        tetris_code, output_console = self.read_files()
        if not tetris_code or not output_console:
            print("[CLIENT] Não foi possível ler os arquivos necessários. Encerrando.")
            return False

        # Passo 2: Criar prompt.txt
        self.create_prompt(tetris_code, output_console)

        # Passo 3: Mover arquivos para history
        self.move_to_history()

        # Passo 4: Enviar prompt.txt para o servidor
        response = self.send_prompt()
        if not response:
            print("[CLIENT] Não foi possível obter uma resposta válida do servidor. Encerrando.")
            return False

        # Passo 5: Extrair apenas o código Python da resposta
        python_code = self.extract_python_code(response)
        if not python_code:
            print("[CLIENT] Resposta inválida do servidor. Encerrando.")
            return False

        # Atualizar tetris.py com o código extraído
        self.update_tetris_code(python_code)

        # Passo 6: Executar tetris.py e salvar a saída em output.txt
        self.execute_tetris()

        return True

    def run_until_completion(self):
        """Executa o loop até que uma condição de parada seja atingida."""
        # Garantir que os arquivos iniciais existam
        self.ensure_initial_files()

        iteration = 1
        while True:
            print(f"\n[CLIENT] Iniciando iteração {iteration}...")
            success = self.run_iteration()
            if not success:
                print("[CLIENT] Condição de parada atingida. Encerrando.")
                break

            # Verificar se o jogo está completo e correto
            with open("tetris.py", "r", encoding="utf-8") as f:
                tetris_code = f.read().strip()
                if "Todos os testes passaram!" in tetris_code:
                    print("[CLIENT] Todos os testes passaram! Jogo completo e correto. Encerrando.")
                    break

            iteration += 1

########################################
# Execução do Cliente
########################################
def main():
    if len(sys.argv) < 2:
        print("Uso: python deepseek_loop.py client")
        sys.exit(1)

    mode = sys.argv[1].lower()
    if mode == "client":
        client = DeepSeekClient(server_url="http://localhost:5000")
        client.run_until_completion()
    else:
        print("Modo inválido. Use 'client'.")

if __name__ == "__main__":
    main()