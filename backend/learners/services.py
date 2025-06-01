# learners/services.py
import requests
from django.conf import settings
import json
import logging
import time

logger = logging.getLogger(__name__)

def generate_ai_response(prompt_text, stream=False):
    """Generate AI response using Together AI API with optional streaming support"""
    logger.info(f"Generating AI response for prompt: {prompt_text[:100]}...")

    headers = {
        "Authorization": f"Bearer {settings.TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    formatted_prompt = f"""You are a helpful AI teacher. Please provide a clear, informative, and educational response to the following question or topic:

{prompt_text}

Please be thorough but concise in your explanation."""

    payload = {
        "model": settings.TOGETHER_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful AI teacher, providing clear and educational responses."},
            {"role": "user", "content": formatted_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500,
        "top_p": 0.8,
        "frequency_penalty": 0.2,
        "presence_penalty": 0.2,
        "stream": stream  # Enable streaming when requested
    }

    try:
        logger.info("Sending request to Together AI API...")
        
        if stream:
            # Streaming response handling
            response = requests.post(
                settings.TOGETHER_API_URL,
                json=payload,
                headers=headers,
                stream=True,
                timeout=30
            )
            
            def generate():
                if response.status_code != 200:
                    error_msg = handle_error_response(response)
                    yield f"data: {json.dumps({'text': error_msg, 'done': True})}\n\n"
                    return

                accumulated_text = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            line_text = line.decode('utf-8')
                            if line_text.startswith('data: '):
                                json_str = line_text[6:]  # Remove 'data: ' prefix
                                if json_str.strip() == '[DONE]':
                                    yield f"data: {json.dumps({'text': '', 'done': True})}\n\n"
                                    break
                                
                                chunk = json.loads(json_str)
                                if 'choices' in chunk and len(chunk['choices']) > 0:
                                    delta = chunk['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        text_chunk = delta['content']
                                        accumulated_text += text_chunk
                                        yield f"data: {json.dumps({'text': text_chunk, 'done': False})}\n\n"
                                        time.sleep(0.05)  # Increased delay from 0.02 to 0.05 seconds for slower typing
                        except Exception as e:
                            logger.error(f"Error processing stream chunk: {str(e)}")
                            continue

            return generate()
        else:
            # Non-streaming response handling
            response = requests.post(
                settings.TOGETHER_API_URL,
                json=payload,
                headers=headers,
                timeout=20
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        ai_response = data["choices"][0]["message"]["content"]
                        logger.info("Successfully generated AI response")
                        return ai_response.strip()
                    else:
                        logger.error(f"Unexpected API response format: {data}")
                        return "I apologize, but I couldn't generate a proper response. Please try asking your question again."
                except (KeyError, IndexError, json.JSONDecodeError) as e:
                    logger.error(f"Error parsing API response: {str(e)}")
                    logger.error(f"Response content: {response.text}")
                    return "I apologize, but there was an error processing the response. Please try again."
            else:
                return handle_error_response(response)
                
    except requests.exceptions.Timeout:
        logger.error("API request timed out")
        return "The AI service is taking too long to respond. Please try again."
    except requests.exceptions.ConnectionError:
        logger.error("Connection to API failed")
        return "Could not connect to the AI service. Please check your internet connection and try again."
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return "An unexpected error occurred. Please try again later."

def handle_error_response(response):
    """Handle different error responses from the API"""
    try:
        if response.status_code == 401:
            logger.error("API authentication failed")
            return "There was an authentication error with the AI service. Please contact support."
        elif response.status_code == 429:
            logger.error("API rate limit exceeded")
            return "The AI service is currently busy. Please wait a moment and try again."
        else:
            logger.error(f"API error {response.status_code}: {response.text}")
            return "I apologize, but the AI service is currently unavailable. Please try again later."
    except Exception as e:
        logger.error(f"Error handling API error response: {str(e)}")
        return "An unexpected error occurred. Please try again later."
