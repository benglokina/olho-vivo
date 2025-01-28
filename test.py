import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig

# Especifica o nome do modelo e a pasta para offload
model_name = "deepseek-ai/deepseek-llm-67b-base"
offload_folder = "./offload_weights"

# Carrega o tokenizador e o modelo com as configurações de offload
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.bfloat16,
    device_map="cuda" if torch.cuda.is_available() else "cpu",
    offload_folder=offload_folder  # Pasta criada para offload de pesos
)

# Configuração de geração
model.generation_config = GenerationConfig.from_pretrained(model_name)
model.generation_config.pad_token_id = model.generation_config.eos_token_id

# Teste de geração com um texto de exemplo
text = "An attention function can be described as mapping a query and a set of key-value pairs to an output, where the query, keys, values, and output are all vectors. The output is"
inputs = tokenizer(text, return_tensors="pt")
outputs = model.generate(**inputs.to(model.device), max_new_tokens=100)

# Decodifica e exibe o resultado
result = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(result)
