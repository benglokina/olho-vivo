from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch
from transformers import TextIteratorStreamer
from threading import Thread
import time

class DeepSeekUnlimited:

    def __init__(self):
        
        model_r1 = "deepseek-ai/DeepSeek-R1"
        model_7b = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
        model_14b = "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"

        model = model_r1

        self.tokenizer = AutoTokenizer.from_pretrained(
            model,
            trust_remote_code=True,
            padding_side="left",  # Crucial para geração longa
            cache_dir="/mnt/d/DeepSeek"
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model,
            device_map="auto",
            quantization_config=BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4"
            ),
            torch_dtype=torch.float16,
            trust_remote_code=True
        )
        self.model.eval()

    def generate(self, prompt):
        messages = [
            {"role": "system", "content": "Você é um expert em Python e Pygame."},
            {"role": "user", "content": prompt}
        ]
        
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt",
            return_attention_mask=True
        ).to(self.model.device)

        # Configuração de geração desbloqueada
        outputs = self.model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_new_tokens=20048,  # Aumente conforme necessário
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
            early_stopping=True  # Para quando atingir conclusão lógica
        )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def generate_unlimited(self, prompt):
        streamer = TextIteratorStreamer(self.tokenizer)
        
        generation_kwargs = dict(
            streamer=streamer,
            max_new_tokens=1_000_000,  # Simbolicamente "ilimitado"
            temperature=0.7,
            top_p=0.9,
            early_stopping=True
        )

        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()

        full_text = ""
        for new_text in streamer:
            full_text += new_text
            #print(new_text, end="", flush=True)
            print(new_text, end="", flush=True)
            # Condição de parada dinâmica
            if "</fim>" in full_text:  # Customize com seu token de parada
                break

        return full_text

    def generate_stream(self, prompt):
        messages = [
            {"role": "system", "content": "Você é um expert em Python e Pygame."},
            {"role": "user", "content": prompt}
        ]
        
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(self.model.device)

        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True
        )

        generation_kwargs = dict(
            input_ids=inputs.input_ids,
            streamer=streamer,
            max_new_tokens=20048,  # Número alto para evitar interrupções
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )

        thread = Thread(target=self.model.generate, kwargs={**generation_kwargs})
        thread.start()

        full_response = ""
        print("\n🚀 Geração Iniciada:\n")
        
        for new_text in streamer:
            full_response += new_text
            print(new_text, end="", flush=True)
        
        return full_response

if __name__ == "__main__":
    generator = DeepSeekUnlimited()
    # Lendo o prompt de um arquivo externo
    with open("prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read().strip()
    start_time = time.time()
    print("🔥 Iniciando geração...")
    #response = generator.generate(prompt)
    response = generator.generate_stream(prompt)
    print(response)
    elapsed_time = time.time() - start_time
    print(f"\n\n✅ Código salvo com sucesso {elapsed_time:.2f} segundos!")
    