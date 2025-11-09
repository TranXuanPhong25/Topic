import requests

URL = "http://127.0.0.1:8080/completion"

system_prompt = (
    "You are a careful medical assistant. "
    "Answer concisely, avoid making final diagnoses, "
    "and always mention red-flag symptoms that require urgent in-person care."
)

user_prompt = (
    "A 25-year-old woman presents with fever and sore throat for 2 days. "
    "No shortness of breath, no rash, no chest pain. "
    "List 3 possible diagnoses with brief reasoning and suggested next steps."
)

full_prompt = f"{system_prompt}\n\nUser: {user_prompt}\nAssistant:"

payload = {
    "prompt": full_prompt,
    "n_predict": 256,      # số token model sinh ra
    "temperature": 0.2,
    "top_k": 40,
    "top_p": 0.9,
    "stream": False        # để trả về một JSON duy nhất
}

resp = requests.post(URL, json=payload, timeout=300)
resp.raise_for_status()

data = resp.json()
print("=== Raw JSON ===")
print(data)
print("\n=== Model output ===")
print(data.get("content", "No content field found"))
