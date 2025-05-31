# learners/services.py
import requests
from django.conf import settings
from django.http import StreamingHttpResponse
import json
import time
import re

def generate_ai_response(prompt_text, stream=False):
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
        "stream": stream
    }

    if not stream:
        response = requests.post(settings.TOGETHER_API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return "Sorry, the AI failed to generate a response."
    else:
        try:
            response = requests.post(settings.TOGETHER_API_URL, json=payload, headers=headers, stream=True)
            if response.status_code != 200:
                yield "Sorry, the AI failed to generate a response."
                return

            buffer = ""
            last_yield_time = time.time()
            min_chunk_delay = 0.15  # 150ms minimum delay between chunks
            sentence_delay = 0.5    # 500ms delay between sentences
            word_delay = 0.08       # 80ms delay between words

            def should_yield_buffer(chunk):
                # Check if we have a complete sentence or significant phrase
                sentence_endings = ['.', '!', '?', ':', ';']
                phrase_endings = [',', '-', ')', '}', ']', '\n']
                
                # If buffer ends with sentence ending, add longer delay
                if any(buffer.rstrip().endswith(end) for end in sentence_endings):
                    time.sleep(sentence_delay)
                    return True
                # If buffer ends with phrase ending, add medium delay
                elif any(buffer.rstrip().endswith(end) for end in phrase_endings):
                    time.sleep(word_delay * 2)
                    return True
                # If we have complete words (space in current chunk), add small delay
                elif ' ' in chunk:
                    time.sleep(word_delay)
                    return True
                return False

            for line in response.iter_lines():
                if not line:
                    continue
                    
                try:
                    line = line.decode('utf-8')
                    if not line.startswith('data: '):
                        continue
                        
                    try:
                        data = json.loads(line[6:])
                        if not data.get("choices") or not len(data["choices"]) > 0:
                            continue
                            
                        if data["choices"][0].get("finish_reason") is not None:
                            if buffer:  # Yield any remaining buffered content
                                time.sleep(sentence_delay)
                                yield buffer
                            break
                        
                        chunk = data["choices"][0].get("delta", {}).get("content", "")
                        if not chunk:
                            continue
                            
                        buffer += chunk
                        
                        # Control streaming pace
                        current_time = time.time()
                        if current_time - last_yield_time < min_chunk_delay:
                            time.sleep(min_chunk_delay - (current_time - last_yield_time))
                        
                        # Yield buffer based on natural language breaks
                        if should_yield_buffer(chunk):
                            yield buffer
                            buffer = ""
                            last_yield_time = time.time()
                    except json.JSONDecodeError:
                        continue
                except UnicodeDecodeError:
                    continue
                    
            if buffer:  # Yield any remaining buffered content
                time.sleep(sentence_delay)
                yield buffer
                
        except Exception as e:
            print(f"Error in generate_ai_response: {str(e)}")
            yield "Sorry, there was an error generating the response."
            return
