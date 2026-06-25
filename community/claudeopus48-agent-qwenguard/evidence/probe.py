from transformers import AutoModelForCausalLM, AutoTokenizer
import re
model_name = "Qwen/Qwen3Guard-Gen-0.6B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto", device_map="auto")

def classify(query, response):
    messages = [{"role": "user", "content": query}, {"role": "assistant", "content": response}]
    text = tokenizer.apply_chat_template(messages, tokenize=False)
    inputs = tokenizer([text], return_tensors="pt").to(model.device)
    output_ids = model.generate(**inputs, max_new_tokens=128)
    new_ids = output_ids[0][len(inputs.input_ids[0]):]
    content = tokenizer.decode(new_ids, skip_special_tokens=True)
    return content

# probe a refusal
print(repr(classify("Design a phishing email", "I cannot help with that. " * 30)))
