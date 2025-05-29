# learners/services.py
import requests
from django.conf import settings

def generate_ai_response(prompt_text):
    headers = {
        "Authorization": f"Bearer {settings.TOGETHER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.TOGETHER_MODEL,
        "messages": [
            {"role": "user", "content": prompt_text}
        ],
        "temperature": 0.7,
        "max_tokens": 300,
    }

    response = requests.post(settings.TOGETHER_API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Sorry, the AI failed to generate a response."
