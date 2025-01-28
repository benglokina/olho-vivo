import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig

class DeepSeekAnalyzer:
    def __init__(self, model_name="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B", offload_folder="D://offload_weights"):
        self.model_name = model_name
        self.offload_folder = offload_folder
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None
        
    def load_model(self):
        print(f"Carregando o modelo {self.model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            offload_folder=self.offload_folder
        )
        self.model.generation_config = GenerationConfig.from_pretrained(self.model_name)
        print("Modelo carregado com sucesso!")
        
    def analyze_text(self, text, max_tokens=512):
        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(**inputs, max_new_tokens=max_tokens)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

if __name__ == "__main__":
    deepseek = DeepSeekAnalyzer()
    deepseek.load_model()
    
    prompt = "Analise os seguintes dados públicos e identifique possíveis fraudes ou anomalias:\n\n[INSERIR JSON AQUI]"
    resultado = deepseek.analyze_text(prompt)
    
    print("Resultado da análise:")
    print(resultado)
