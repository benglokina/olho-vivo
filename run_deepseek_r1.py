import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    AutoConfig,
    BitsAndBytesConfig,
    TextIteratorStreamer
)
from threading import Thread

class DeepSeekR1:
    def __init__(self):
        self.model_name = "deepseek-ai/DeepSeek-R1"
        
        # Configuração de Quantização 4-bit desejada
        self.quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="bitsandbytes_4bit"
        )
        
        # Carrega a configuração do modelo
        config = AutoConfig.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            # Define a pasta onde o config será armazenado
            cache_dir="/mnt/d/DeepSeek"
        )
        
        # Remove ou zera o 'quantization_config' que vem definido como 'fp8' no repositório
        if hasattr(config, "quantization_config"):
            config.quantization_config = None
        
        # Carrega o tokenizer, apontando para a mesma pasta de cache
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            padding_side="left",
            cache_dir="D:/DeepSeek"
        )
        
        # Carrega o modelo com a configuração alterada e cache apontado
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            config=config,
            device_map="auto",
            quantization_config=self.quant_config,
            torch_dtype=torch.float16,
            trust_remote_code=True,
            cache_dir="D:/DeepSeek"
        )
        self.model.eval()

    def generate(self, prompt):
        # Prepara o prompt para o modelo
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")

        # Cria um streamer para geração token a token
        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True)
        
        generation_kwargs = dict(
            inputs=inputs,
            streamer=streamer,
            max_new_tokens=2000,
            temperature=0.7,
            top_p=0.9
        )
        
        # Geração em outra thread para podermos iterar nos tokens
        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()
        
        generated_text = ""
        # Captura o texto à medida que sai
        for new_text in streamer:
            generated_text += new_text
            print(new_text, end="", flush=True)
            
        return generated_text

if __name__ == "__main__":
    generator = DeepSeekR1()
    prompt = "Recrie o jogo snake em python e pygame."
    print("\n🔥 Resposta do Modelo:\n")
    generator.generate(prompt)
