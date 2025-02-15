import os
import time
import torch
from threading import Thread
from accelerate import init_empty_weights, load_checkpoint_and_dispatch
from transformers import (
    AutoConfig,
    AutoTokenizer,
    AutoModelForCausalLM,
    TextIteratorStreamer
)
import glob

MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"  # Modelo 32B
CACHE_DIR = "./DeepSeek"  # Diretório de cache atualizado

def get_checkpoint_path(model_name, cache_dir):
    """
    Procura no cache pelo snapshot mais recente do repositório.
    O modelo é normalmente armazenado em:
      {cache_dir}/models--<model_name com '/' substituído por '--'>/snapshots/<commit_hash>
    """
    folder_name = "models--" + model_name.replace("/", "--")
    snapshot_dir = os.path.join(cache_dir, folder_name, "snapshots")
    snapshot_candidates = glob.glob(os.path.join(snapshot_dir, "*"))
    if not snapshot_candidates:
        raise ValueError(f"Não foi possível encontrar snapshots em {snapshot_dir}.")
    checkpoint_path = sorted(snapshot_candidates)[-1]
    return checkpoint_path

class DeepSeekGenerator:
    def __init__(self):
        print(f"[INFO] Carregando tokenizer do modelo: {MODEL_NAME}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME,
            trust_remote_code=True,
            padding_side="left",
            cache_dir=CACHE_DIR
        )

        print("[INFO] Carregando config do modelo (sem quantization_config)...")
        config = AutoConfig.from_pretrained(
            MODEL_NAME,
            trust_remote_code=True,
            cache_dir=CACHE_DIR
        )
        if hasattr(config, "quantization_config"):
            config.quantization_config = None

        print("[INFO] Criando modelo vazio com init_empty_weights()...")
        with init_empty_weights():
            self.model = AutoModelForCausalLM.from_config(
                config,
                trust_remote_code=True,
                torch_dtype=torch.float16
            )

        checkpoint_path = get_checkpoint_path(MODEL_NAME, CACHE_DIR)
        print(f"[INFO] Snapshot encontrado: {checkpoint_path}")

        print("[INFO] Carregando e despachando pesos (offload GPU/CPU) com Accelerate...")
        self.model = load_checkpoint_and_dispatch(
            self.model,
            checkpoint=checkpoint_path,
            device_map="auto",         # A Accelerate decide GPU vs CPU
            max_memory={
                0: "12GiB",            # Ajuste conforme sua VRAM
                "cpu": "32GiB"         # Ajuste conforme sua RAM
            },
            dtype=torch.float16,
            offload_folder="offload_weights",
            no_split_module_classes=[]
        )

        self.model.eval()

    def generate_stream(self, prompt):
        messages = [
            {"role": "system", "content": "Você é um expert em Python e Pygame."},
            {"role": "user",   "content": prompt}
        ]
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(device)

        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True
        )

        generation_kwargs = dict(
            input_ids=inputs.input_ids,
            streamer=streamer,
            max_new_tokens=1024,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )

        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()

        full_response = ""
        print("\n🚀 Geração Iniciada:\n")
        for new_text in streamer:
            full_response += new_text
            print(new_text, end="", flush=True)
        return full_response

def main():
    generator = DeepSeekGenerator()

    with open("prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read().strip()

    start = time.time()
    print("\n🔥 Iniciando geração...\n")
    response = generator.generate_stream(prompt)

    print("\n\nResposta final:\n", response)
    print(f"\n✅ Geração concluída em {time.time() - start:.2f}s")

if __name__ == "__main__":
    main()
