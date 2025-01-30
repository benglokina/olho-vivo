from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch
from transformers import TextIteratorStreamer
from threading import Thread

class DeepSeekUnlimited:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            #"deepseek-ai/DeepSeek-R1",
            #"deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
            "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
            trust_remote_code=True,
            padding_side="left"  # Crucial para geração longa
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
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
            input.input_ids,
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
            print(new_text, end="", flush=True)
            # Condição de parada dinâmica
            if "</fim>" in full_text:  # Customize com seu token de parada
                break

        return full_text

if __name__ == "__main__":
    generator = DeepSeekUnlimited()
    resposta = generator.generate("Código FUNCIONAL de tetris em python, com as peças basicas, mover as peças para o lado, rotacionar as peças, acelerar descida e limpar linhas.")
    print(resposta)