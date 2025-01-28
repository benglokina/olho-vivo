import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class DeepSeekModel:
    def __init__(self, model_name="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B", offload_folder="D://offload_weights"):
        self.model_name = model_name
        self.offload_folder = offload_folder
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Configurações para otimização do uso da GPU e RAM
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        torch.set_grad_enabled(False)  # Desativa gradientes para economizar memória

        self.load_model()

    def load_model(self):
        print(f"Carregando o modelo {self.model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            offload_folder=self.offload_folder
        )

        # Aplicar otimização adicional ao modelo
        self.model = torch.compile(self.model)

        print("Modelo carregado com sucesso!")

    def generate_response_stream(self, prompt, max_new_tokens=20000):
        print("Gerando resposta em tempo real...")
        start_time = time.time()

        # Preparar entradas
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        # Estado inicial para o cache do modelo
        generated_ids = inputs["input_ids"]

        response = ""

        for _ in range(max_new_tokens):
            outputs = self.model.generate(
                input_ids=generated_ids,
                max_new_tokens=1,  # Gera um token por vez
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.pad_token_id,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.2,
                use_cache=True
            )

            # Selecionar o último token gerado
            new_token_id = outputs[0, -1].unsqueeze(0)

            # Decodificar o novo token
            new_token_decoded = self.tokenizer.decode(new_token_id, skip_special_tokens=True)

            # Adicionar ao texto gerado
            response += new_token_decoded

            # Imprimir o token gerado em tempo real
            print(new_token_decoded, end="", flush=True)

            # Atualizar a sequência para o próximo passo
            generated_ids = torch.cat([generated_ids, new_token_id.unsqueeze(0)], dim=-1)

            # Interromper se o token de fim for gerado
            if new_token_id.item() == self.tokenizer.eos_token_id:
                break

        end_time = time.time()
        elapsed_time = end_time - start_time
        print("\n\nGeração concluída.")
        return response, elapsed_time

if __name__ == "__main__":
    deepseek = DeepSeekModel()

    # Testando envio de prompt mais simples para geração contínua
    prompt = "Por favor, escreva um programa em Python para criar um jogo de Tetris. Explique cada etapa com comentários no código."

    print(f"Dispositivo atual: {deepseek.device}")

    # Gerar resposta com streaming
    resposta, tempo = deepseek.generate_response_stream(prompt)

    print(f"\nTempo de execução: {tempo:.2f} segundos")
