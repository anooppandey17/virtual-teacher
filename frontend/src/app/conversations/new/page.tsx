'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import ClientNavbar from '../../components/ClientNavbar';
import toast from 'react-hot-toast';

interface Message {
  id: number;
  text: string;
  role: 'user' | 'assistant';
  created_at: string;
}

export default function NewConversationPage() {
  const [newMessage, setNewMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [streamingText, setStreamingText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [visibleChars, setVisibleChars] = useState(0);
  const router = useRouter();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const scrollToBottom = () => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const fetchConversationMessages = async (convId: number) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/learners/conversations/${convId}/`, {
        headers: {
          Authorization: `Token ${token}`,
        },
      });

      if (response.ok) {
        const conversation = await response.json();
        if (conversation.responses) {
          setMessages(conversation.responses.map((resp: any) => ({
            id: resp.id,
            text: resp.text,
            role: resp.role,
            created_at: resp.created_at,
          })));
        }
      }
    } catch (err) {
      console.error('Error fetching conversation messages:', err);
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingText]);

  // Debug useEffect to track streaming state
  useEffect(() => {
    console.log('Streaming state changed - isStreaming:', isStreaming, 'streamingText:', streamingText);
  }, [isStreaming, streamingText]);

  // Force scroll when streaming starts
  useEffect(() => {
    if (isStreaming) {
      scrollToBottom();
    }
  }, [isStreaming]);

  const handleStop = async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    
    // Save the partial response to the database
    if (streamingText.trim() && conversationId) {
      try {
        const token = localStorage.getItem('token');
        if (token) {
          await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/learners/conversations/${conversationId}/messages/`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Token ${token}`,
            },
            body: JSON.stringify({ text: streamingText }),
          });
        }
      } catch (err) {
        console.error('Error saving partial response:', err);
      }
    }

    // Add the partial response as a message
    if (streamingText.trim()) {
      const aiMessage = {
        id: Date.now(),
        text: streamingText,
        role: 'assistant' as const,
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, aiMessage]);
    }

    // Reset streaming state
    setIsStreaming(false);
    setStreamingText('');
    setVisibleChars(0);
    setSending(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || sending) return;

    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    setSending(true);
    setError('');
    setIsStreaming(true);
    setStreamingText('');
    setVisibleChars(0);
    console.log('Streaming started'); // Debug log
    
    // Store the message text and clear input immediately
    const messageText = newMessage;
    setNewMessage('');
    
    // Create temporary message ID for error handling
    const tempMessageId = Date.now();

    // Create new AbortController for this request
    abortControllerRef.current = new AbortController();

    try {
      let response;
      
      if (conversationId) {
        // Conversation already exists, send message to existing conversation
        // Add the user's message immediately for better UX
        const tempUserMessage = {
          id: tempMessageId,
          text: messageText,
          role: 'user' as const,
          created_at: new Date().toISOString(),
        };
        setMessages(prev => [...prev, tempUserMessage]);
        
        response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/learners/conversations/${conversationId}/messages/?stream=true`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Token ${token}`,
          },
          body: JSON.stringify({ text: messageText }),
          signal: abortControllerRef.current.signal,
        });
      } else {
        // Create new conversation with the first message
        // Don't add user message locally since backend will create it
        
        // Create conversation without generating AI response (let frontend handle streaming)
        const createResponse = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/learners/conversations/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Token ${token}`,
          },
          body: JSON.stringify({ prompt: messageText }), // Use 'prompt' as expected by serializer
          signal: abortControllerRef.current.signal,
        });

        if (!createResponse.ok) {
          throw new Error('Failed to create conversation');
        }

        const conversation = await createResponse.json();
        setConversationId(conversation.id);
        
        // Update the URL to reflect the new conversation ID
        router.replace(`/conversations/${conversation.id}`);
        
        // Fetch the conversation messages to display the user message created by backend
        await fetchConversationMessages(conversation.id);
        
        // Get the streaming response for the AI reply
        response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/learners/conversations/${conversation.id}/messages/?stream=true`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Token ${token}`,
          },
          body: JSON.stringify({ text: messageText }), // Send the actual message text
          signal: abortControllerRef.current.signal,
        });
      }

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Stream not available');
      }

      let accumulatedText = '';
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }

        // Convert the chunk to text
        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(5));
              if (data.done) {
                // Save the complete message to the conversation
                const aiMessage = {
                  id: Date.now(),
                  text: accumulatedText,
                  role: 'assistant' as const,
                  created_at: new Date().toISOString(),
                };

                setMessages(prev => [...prev, aiMessage]);
                setIsStreaming(false);
                console.log('Streaming ended, final text:', accumulatedText); // Debug log
                break;
              } else {
                // Add character with a small delay for smooth typing effect
                accumulatedText += data.text;
                setStreamingText(accumulatedText);
                setVisibleChars(prev => prev + 1);
                console.log('Streaming text updated:', accumulatedText);
                
                // Add a small delay for realistic typing speed
                await new Promise(resolve => setTimeout(resolve, 30));
              }
            } catch (e) {
              console.error('Error parsing streaming data:', e);
            }
          }
        }
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        console.log('Request was aborted');
        // Don't show error for aborted requests
        return;
      }
      console.error('Error in handleSubmit:', err);
      setError('Error: Failed to process the response. Please try again.');
      // Remove the temporary message if there was an error
      setMessages(prev => prev.filter(m => m.id !== tempMessageId));
    } finally {
      setSending(false);
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  };

  const formatMessage = (text: any): string => {
    if (typeof text === 'string') return text;
    return 'Error: Could not display message';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <ClientNavbar />
      <div className="max-w-4xl mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">New Conversation</h1>
        
        <div className="bg-white rounded-lg shadow p-4 mb-4 min-h-[400px] max-h-[600px] overflow-y-auto">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 mt-8">
              <p className="text-lg mb-2">👋 Welcome to your new conversation!</p>
              <p className="text-sm">Type your first message below to get started.</p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`mb-4 ${
                  message.role === 'user' ? 'text-right' : 'text-left'
                }`}
              >
                <div
                  className={`inline-block rounded-lg px-4 py-2 max-w-[70%] ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-800'
                  }`}
                >
                  <p className="break-words whitespace-pre-wrap">{formatMessage(message.text)}</p>
                  <p className="text-xs mt-1 opacity-75">
                    {new Date(message.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            ))
          )}
          
          {isStreaming && (
            <div className="text-left mb-4">
              <div className="inline-block rounded-lg px-4 py-2 bg-gray-200 text-gray-800 border-2 border-blue-300">
                <p className="break-words whitespace-pre-wrap">
                  {streamingText ? (
                    <>
                      {streamingText.slice(0, visibleChars)}
                      <span className="cursor-blink">|</span>
                    </>
                  ) : (
                    'AI is thinking...'
                  )}
                </p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-lg flex items-center justify-between">
            <span>{error}</span>
            <button
              onClick={() => setError('')}
              className="text-red-400 hover:text-red-600"
            >
              ✕
            </button>
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type your message..."
            disabled={sending || isStreaming}
            className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          <button
            type={isStreaming ? 'button' : 'submit'}
            onClick={isStreaming ? handleStop : undefined}
            disabled={(!newMessage.trim() && !isStreaming) || (sending && !isStreaming)}
            className={`px-6 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed ${
              isStreaming 
                ? 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500' 
                : 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500'
            }`}
          >
            {isStreaming ? 'Stop' : (sending ? 'Teacher is thinking...' : 'Send')}
          </button>
        </form>
      </div>
    </div>
  );
} 