import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

LLM_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
device = "mps" if torch.backends.mps.is_available() else "cpu"
print("Device:", device)

tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
print("Tokenizer OK")

llm = AutoModelForCausalLM.from_pretrained(LLM_MODEL, dtype=torch.float32)
print("Modelo carregado em CPU (float32), sem .to(device) ainda")

llm = llm.to(device)
print("Modelo movido para", device, "com sucesso")

messages = [{"role": "user", "content": "Dis bonjour en une phrase."}]

inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    return_tensors="pt",
    return_dict=True
).to(device)

print("Input tokenizado, gerando...")

output = llm.generate(**inputs, max_new_tokens=30)
print(tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True))