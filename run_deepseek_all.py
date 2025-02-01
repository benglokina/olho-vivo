import time
from threading import Thread
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TextIteratorStreamer
)

class DeepSeekGenerator:
    def __init__(self):
        # Escolha o modelo desejado: "7b", "14b" ou "32b"
        self.model_choice = "7b"  # Altere para "14b" ou "32b" conforme necessário

        # Dicionário de nomes de modelos
        models = {
            "7b": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
            "14b": "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
            "32b": "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
        }

        if self.model_choice not in models:
            raise ValueError("Opção inválida para model_choice. Use '7b', '14b' ou '32b'.")

        self.model_name = models[self.model_choice]

        # Diretório de cache para armazenar os modelos baixados
        cache_dir = "./DeepSeek"

        # Carrega o tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            padding_side="left",  # Importante para geração longa
            cache_dir=cache_dir
        )

        # Configuração de quantização para os modelos (usando nf4 para 4-bit)
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_enable_fp32_cpu_offload=True  # Offload para CPU se necessário
        )

        # Carrega o modelo com a configuração de quantização
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",
            quantization_config=quant_config,
            torch_dtype=torch.float16,
            trust_remote_code=True,
            cache_dir=cache_dir
        )

        # Coloca o modelo em modo de avaliação
        self.model.eval()

    def generate_stream(self, prompt):
        # Prepara as mensagens iniciais (template de chat)
        messages = [
            {"role": "system", "content": "Você é um expert em Python e Pygame."},
            {"role": "user",   "content": prompt}
        ]

        # Aplica o template de chat para formatar o prompt
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # Prepara os inputs e envia para o dispositivo do modelo
        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(self.model.device)

        # Configura o streamer para gerar tokens de forma iterativa
        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True
        )

        generation_kwargs = dict(
            input_ids=inputs.input_ids,
            streamer=streamer,
            max_new_tokens=20048,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )

        # Inicia a geração em uma thread separada
        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()

        full_response = ""
        print("\n🚀 Geração Iniciada:\n")
        for new_text in streamer:
            full_response += new_text
            print(new_text, end="", flush=True)
        return full_response


if __name__ == "__main__":
    # Instancia o gerador (a escolha do modelo é definida internamente)
    generator = DeepSeekGenerator()
    
    # Lê o prompt do arquivo prompt.txt
    with open("prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read().strip()
    
    start_time = time.time()
    print("🔥 Iniciando geração...\n")
    
    response = generator.generate_stream(prompt)
    
    print("\n\nResposta final:\n", response)
    elapsed_time = time.time() - start_time
    print(f"\n\n✅ Geração concluída em {elapsed_time:.2f} segundos!")
