import os
import shutil
import subprocess
import requests
import re
import sys


class LiberActivaClient:
    def __init__(self, server_url="http://localhost:5000", history_dir="history"):
        self.server_url = server_url
        self.history_dir = history_dir
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)

    def ensure_initial_files(self, script_path="script.py", output_path="output.txt", prompt_output_path="prompt_output.txt"):
        """Garante que os arquivos script.py, output.txt e prompt_output.txt existam."""
        for file_path in [script_path, output_path, prompt_output_path]:
            if not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("# Conteúdo inicial\n")
                print(f"[LIBERACTIVA] Arquivo {file_path} criado com conteúdo inicial.")

    def read_files(self, script_path="script.py", output_path="output.txt", prompt_output_path="prompt_output.txt"):
        """Lê os arquivos script.py, output.txt e prompt_output.txt."""
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                script_code = f.read().strip()
                print(f"[DEBUG] Arquivo {script_path} lido com sucesso.")
            with open(output_path, "r", encoding="utf-8") as f:
                output_console = f.read().strip()
                print(f"[DEBUG] Arquivo {output_path} lido com sucesso.")
            with open(prompt_output_path, "r", encoding="utf-8") as f:
                prompt_output = f.read().strip()
                print(f"[DEBUG] Arquivo {prompt_output_path} lido com sucesso.")
            return script_code, output_console, prompt_output
        except Exception as e:
            print(f"[LIBERACTIVA] Erro ao ler arquivos: {e}")
            return None, None, None

    def create_prompt(self, script_code, output_console, prompt_output):
        """Cria o arquivo prompt.txt com base no template e nos dados fornecidos."""
        try:
            with open("prompt_template.txt", "r", encoding="utf-8") as f:
                template = f.read().strip()
            prompt_content = template.format(
                script_code=script_code,
                output_console=output_console,
                prompt_output=prompt_output
            )
            with open("prompt.txt", "w", encoding="utf-8") as f:
                f.write(prompt_content)
            print("[LIBERACTIVA] Arquivo prompt.txt criado com sucesso.")
        except Exception as e:
            print(f"[LIBERACTIVA] Erro ao criar o prompt: {e}")

    def move_to_history(self, script_path="script.py", output_path="output.txt", prompt_output_path="prompt_output.txt"):
        """Move os arquivos script.py, output.txt e prompt_output.txt para a pasta history."""
        files = os.listdir(self.history_dir)
        script_count = len([f for f in files if f.startswith("script_")])
        new_script_name = f"script_{script_count + 1:03d}.py"
        new_output_name = f"output_{script_count + 1:03d}.txt"
        new_prompt_output_name = f"prompt_output_{script_count + 1:03d}.txt"
        shutil.move(script_path, os.path.join(self.history_dir, new_script_name))
        shutil.move(output_path, os.path.join(self.history_dir, new_output_name))
        shutil.move(prompt_output_path, os.path.join(self.history_dir, new_prompt_output_name))
        print(f"[LIBERACTIVA] Arquivos movidos para history: {new_script_name}, {new_output_name}, {new_prompt_output_name}")
        # Recriar arquivos após movê-los para a pasta history
        self.ensure_initial_files()

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
                print(f"[LIBERACTIVA] Erro no servidor: {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"[LIBERACTIVA] Exceção na requisição ao servidor: {e}")
            return None

    def extract_python_code(self, response):
        """
        Extrai apenas o primeiro bloco de código Python da resposta do servidor.
        Assume que o código está entre ```python e ```.
        """
        code_pattern = r"```python(.*?)```"
        matches = re.findall(code_pattern, response, re.DOTALL)
        if matches:
            return matches[0].strip()
        else:
            print("[LIBERACTIVA] Não foi possível encontrar código Python na resposta. Continuando sem código.")
            print(f"[DEBUG] Resposta completa do servidor:\n{response}")
            return None

    def extract_and_execute_bash_commands(self, response):
        """
        Extrai comandos Bash da resposta do servidor e os executa na ordem informada.
        Assume que os comandos estão entre ```bash e ```.
        """
        bash_pattern = r"```bash(.*?)```"
        matches = re.findall(bash_pattern, response, re.DOTALL)
        bash_outputs = []

        for i, match in enumerate(matches):
            command = match.strip()
            print(f"[LIBERACTIVA] Executando comando Bash #{i + 1}: {command}")
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )
                output = result.stdout
                if result.stderr:
                    output += "\nERRO:\n" + result.stderr
                bash_outputs.append(output)
                print(f"[LIBERACTIVA] Saída do comando Bash #{i + 1}:\n{output}")
            except Exception as e:
                error_message = f"[LIBERACTIVA] Erro ao executar comando Bash #{i + 1}: {e}"
                print(error_message)
                bash_outputs.append(error_message)

        return bash_outputs

    def update_files(self, python_code, response):
        """Atualiza os arquivos script.py e prompt_output.txt com o código gerado pelo servidor."""
        if python_code:
            with open("script.py", "w", encoding="utf-8") as f:
                f.write(python_code)
            print("[LIBERACTIVA] Arquivo script.py atualizado com sucesso.")
        with open("prompt_output.txt", "w", encoding="utf-8") as f:
            f.write(response)
        print("[LIBERACTIVA] Arquivo prompt_output.txt atualizado com sucesso.")

    def execute_script(self):
        """Executa o arquivo script.py com um timeout e salva a saída em output.txt."""
        try:
            TIMEOUT_SECONDS = 30
            result = subprocess.run(
                ["python", "script.py"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=TIMEOUT_SECONDS
            )
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write(result.stdout)
                if result.stderr:
                    f.write("\nERRO:\n" + result.stderr)
            print("[LIBERACTIVA] Execução do script.py concluída. Saída salva em output.txt.")
        except subprocess.TimeoutExpired:
            error_message = f"[LIBERACTIVA] Erro: O script script.py excedeu o tempo limite de {TIMEOUT_SECONDS} segundos."
            print(error_message)
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write(error_message + "\n")
        except Exception as e:
            print(f"[LIBERACTIVA] Erro ao executar script.py: {e}")
            with open("output.txt", "w", encoding="utf-8") as f:
                f.write(f"Erro ao executar o código: {e}\n")

    def run_iteration(self):
        """Executa uma iteração completa do processo."""
        # Garantir que os arquivos existam antes de prosseguir
        self.ensure_initial_files()

        # Passo 1: Ler arquivos script.py e output.txt
        script_code, output_console, prompt_output = self.read_files()
        if not script_code or not output_console or not prompt_output:
            print("[LIBERACTIVA] Não foi possível ler os arquivos necessários. Encerrando.")
            return False

        # Passo 2: Criar prompt.txt
        self.create_prompt(script_code, output_console, prompt_output)

        # Passo 3: Enviar prompt.txt para o servidor
        response = self.send_prompt()
        if not response:
            print("[LIBERACTIVA] Não foi possível obter uma resposta válida do servidor. Encerrando.")
            return False

        # Passo 4: Extrair código Python da resposta
        python_code = self.extract_python_code(response)

        # Passo 5: Extrair e executar comandos Bash
        bash_outputs = self.extract_and_execute_bash_commands(response)

        # Atualizar script.py apenas se houver código Python
        self.update_files(python_code, response)

        # Passo 6: Executar script.py e salvar a saída em output.txt
        self.execute_script()

        # Move arquivos apenas em caso de sucesso
        self.move_to_history()

        # Verifica se o script está funcionando corretamente
        if not os.path.exists("output.txt"):
            print("[LIBERACTIVA] Arquivo output.txt não encontrado. Continuando sem verificar a saída.")
            return True

        with open("output.txt", "r", encoding="utf-8") as f:
            output_console = f.read().strip()

        if "Todos os testes passaram!" in output_console:
            print("[LIBERACTIVA] Todos os testes passaram! Encerrando.")
            return False

        return True

    def run_until_completion(self):
        """Executa o loop até que uma condição de parada seja atingida."""
        self.ensure_initial_files()
        iteration = 1
        max_iterations = 1000
        while iteration <= max_iterations:
            print(f"\n[LIBERACTIVA] Iniciando iteração {iteration}...")
            success = self.run_iteration()
            if not success:
                print("[LIBERACTIVA] Condição de parada atingida. Encerrando.")
                break
            iteration += 1
        if iteration > max_iterations:
            print("[LIBERACTIVA] Número máximo de iterações atingido. Encerrando.")


def main():
    if len(sys.argv) < 2:
        print("Uso: python liberactiva_client.py client")
        sys.exit(1)
    mode = sys.argv[1].lower()
    if mode == "client":
        client = LiberActivaClient(server_url="http://localhost:5000")
        client.run_until_completion()
    else:
        print("Modo inválido. Use 'client'.")


if __name__ == "__main__":
    main()