# learners/services.py
import requests
from django.conf import settings
import json
import logging
import random
from datetime import datetime

logger = logging.getLogger(__name__)

def get_greeting():
    """Get appropriate greeting based on current time"""
    current_hour = datetime.now().hour
    
    greetings = {
        'morning': ["Good morning", "Good morning!", "Hi there! Good morning", "Hello! Good morning"],
        'afternoon': ["Good afternoon", "Good afternoon!", "Hi there! Good afternoon", "Hello! Good afternoon"],
        'evening': ["Good evening", "Good evening!", "Hi there! Good evening", "Hello! Good evening"],
        'night': ["Good night", "Good night!", "Hi there! Good night", "Hello! Good night"]
    }
    
    if 5 <= current_hour < 12:
        return random.choice(greetings['morning'])
    elif 12 <= current_hour < 17:
        return random.choice(greetings['afternoon'])
    elif 17 <= current_hour < 21:
        return random.choice(greetings['evening'])
    else:
        return random.choice(greetings['night'])

def get_grade_level_context(grade):
    """Get context about the user's grade level for appropriate response complexity"""
    grade_contexts = {
        '1': "You are teaching a Grade 1 student (6-7 years old). Use very simple words, short sentences, and basic concepts. Keep responses brief and use lots of examples. For greetings, just respond with a simple greeting back.",
        '2': "You are teaching a Grade 2 student (7-8 years old). Use simple explanations with basic vocabulary. Keep responses concise and clear. For greetings, respond naturally without explanations.",
        '3': "You are teaching a Grade 3 student (8-9 years old). Use clear explanations with age-appropriate vocabulary. Keep responses focused and practical. For greetings, respond naturally.",
        '4': "You are teaching a Grade 4 student (9-10 years old). Use intermediate vocabulary with clear explanations. Keep responses thorough but concise. For greetings, respond naturally.",
        '5': "You are teaching a Grade 5 student (10-11 years old). Use varied vocabulary with comprehensive explanations. Keep responses engaging but not overly elaborate. For greetings, respond naturally.",
        '6': "You are teaching a Grade 6 student (11-12 years old). Use advanced vocabulary with thorough explanations. Encourage critical thinking. For greetings, respond naturally.",
        '7': "You are teaching a Grade 7 student (12-13 years old). Use academic vocabulary with sophisticated explanations. Help develop analytical skills. For greetings, respond naturally.",
        '8': "You are teaching a Grade 8 student (13-14 years old). Use complex concepts with detailed explanations. Encourage deeper understanding. For greetings, respond naturally.",
        '9': "You are teaching a Grade 9 student (14-15 years old). Use specialized vocabulary with advanced explanations. Prepare for higher-level thinking. For greetings, respond naturally.",
        '10': "You are teaching a Grade 10 student (15-16 years old). Use academic language with comprehensive explanations. Encourage independent analysis. For greetings, respond naturally.",
        '11': "You are teaching a Grade 11 student (16-17 years old). Use college-level vocabulary with sophisticated explanations. Develop advanced critical thinking. For greetings, respond naturally.",
        '12': "You are teaching a Grade 12 student (17-18 years old). Use university-level concepts with advanced explanations. Prepare for higher education. For greetings, respond naturally."
    }
    return grade_contexts.get(grade, "Provide clear and educational responses appropriate for the student's level. For greetings, respond naturally.")

def is_greeting_message(text):
    """Check if the message is a greeting"""
    greeting_indicators = [
        'hello', 'hi', 'hey', 'good morning', 'good afternoon', 
        'good evening', 'good night', 'how are you', 'howdy',
        'greetings', 'salutations', 'good day', 'morning', 'afternoon',
        'evening', 'night', 'sup', 'what\'s up', 'yo'
    ]
    
    text_lower = text.lower().strip()
    return any(indicator in text_lower for indicator in greeting_indicators)

def get_simple_greeting_response(user_greeting, greeting):
    """Get a simple, natural response to a greeting"""
    user_greeting_lower = user_greeting.lower().strip()
    
    # Simple, natural responses based on the user's greeting
    if 'good morning' in user_greeting_lower:
        return f"{greeting}! What would you like to learn about today?"
    elif 'good afternoon' in user_greeting_lower:
        return f"{greeting}! What would you like to learn about today?"
    elif 'good evening' in user_greeting_lower:
        return f"{greeting}! What would you like to learn about today?"
    elif 'good night' in user_greeting_lower:
        return f"{greeting}! What would you like to learn about today?"
    elif 'hello' in user_greeting_lower:
        return f"{greeting}! What would you like to learn about today?"
    elif 'hi' in user_greeting_lower:
        return f"{greeting}! What would you like to learn about today?"
    elif 'hey' in user_greeting_lower:
        return f"{greeting}! What would you like to learn about today?"
    elif 'how are you' in user_greeting_lower:
        return f"{greeting}! I'm doing well. What would you like to learn about today?"
    else:
        return f"{greeting}! What would you like to learn about today?"

def format_conversation_history(conversation_history, max_messages=10):
    """Format conversation history for AI context, prioritizing recent and relevant messages"""
    if not conversation_history or len(conversation_history) == 0:
        return ""
    
    # Take the most recent messages, but ensure we have a good context
    recent_messages = conversation_history[-max_messages:]
    
    # Format the conversation history
    formatted_history = "\n\nPrevious conversation:\n"
    for msg in recent_messages:
        role_label = "Student" if msg['role'] == 'user' else "Teacher"
        # Truncate very long messages to avoid token limits
        text = msg['text'][:200] + "..." if len(msg['text']) > 200 else msg['text']
        formatted_history += f"{role_label}: {text}\n"
    
    return formatted_history

def generate_ai_response(prompt_text, stream=False, user_grade=None, conversation_history=None):
    """Generate AI response using Together AI API with optional streaming support and grade-appropriate content"""
    logger.info(f"Generating AI response for prompt: {prompt_text[:100]}...")

    headers = {
        "Authorization": f"Bearer {settings.TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Get appropriate greeting
    greeting = get_greeting()
    
    # Check if this is a greeting message
    is_greeting = is_greeting_message(prompt_text)
    
    if is_greeting:
        # For greetings, provide a simple, natural response
        simple_response = get_simple_greeting_response(prompt_text, greeting)
        
        if stream:
            # For streaming, yield the simple response character by character
            def generate_simple_response():
                for char in simple_response:
                    yield f"data: {json.dumps({'text': char, 'done': False})}\n\n"
                yield f"data: {json.dumps({'text': '', 'done': True})}\n\n"
            return generate_simple_response()
        else:
            # For non-streaming, return the simple response directly
            return simple_response
    
    # Get grade-appropriate context for non-greeting messages
    grade_context = get_grade_level_context(user_grade) if user_grade else "Provide clear and educational responses appropriate for the student's level."
    
    # Build conversation context
    conversation_context = format_conversation_history(conversation_history)
    
    # For regular questions, provide educational responses with context
    formatted_prompt = f"""{greeting}! I'm your AI teacher. {grade_context}

{conversation_context}Current question/topic: {prompt_text}

Provide a clear, informative, and educational response. Consider the conversation context and build upon previous discussions when relevant.

Remember to:
- Use language and concepts appropriate for the student's grade level
- Be encouraging and supportive
- Provide thorough but concise explanations
- Use examples when helpful
- Keep the response engaging and educational
- Reference previous parts of the conversation when relevant
- Don't be overly elaborate unless the topic requires it
- If the student is asking follow-up questions, build upon what was discussed before
- Be direct and natural - don't repeat phrases like 'I'm happy to help' or 'I'm here to assist'"""

    payload = {
        "model": settings.TOGETHER_MODEL,
        "messages": [
            {"role": "system", "content": f"You are a knowledgeable AI teacher. {grade_context} Provide clear, direct educational responses. Don't use repetitive phrases like 'I'm happy to help' or 'I'm here to assist you' - just teach naturally."},
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
                                        # Send each character individually for smooth typing animation
                                        for char in text_chunk:
                                            yield f"data: {json.dumps({'text': char, 'done': False})}\n\n"
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
                        return f"{greeting}! I apologize, but I couldn't generate a proper response. Please try asking your question again."
                except (KeyError, IndexError, json.JSONDecodeError) as e:
                    logger.error(f"Error parsing API response: {str(e)}")
                    logger.error(f"Response content: {response.text}")
                    return f"{greeting}! I apologize, but there was an error processing the response. Please try again."
            else:
                return handle_error_response(response)
                
    except requests.exceptions.Timeout:
        logger.error("API request timed out")
        return f"{greeting}! The service is taking too long to respond. Please try again."
    except requests.exceptions.ConnectionError:
        logger.error("Connection to API failed")
        return f"{greeting}! It seems you are not connected to the internet."
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return f"{greeting}! An unexpected error occurred. Please try again later."

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
