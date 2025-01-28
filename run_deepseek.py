import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig

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
        
        print("Modelo carregado com sucesso!")
    
    def generate_response(self, prompt, max_new_tokens=500):
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

if __name__ == "__main__":
    deepseek = DeepSeekModel()
    
    # Testando envio de prompt genérico
    prompt = "Gostaria de uam sogestao de projeto para uilizar IA para promover mais transparecias nas contas publicas. O projeto será tocado por 1 unico desenvolvedor com poucas horas disponiveis e pouco recurso financeiro disponivel, o operador tem um um pc com processador r5 5600x e uma 3060, e tem conhecimento em python java c++ e um pouco de experiencia com ia."
    resposta = deepseek.generate_response(prompt)
    print("Resposta do modelo:")
    print(resposta)
