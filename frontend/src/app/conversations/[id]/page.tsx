'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import ClientNavbar from '../../components/ClientNavbar';

interface Message {
  id: number;
  text: string;
  role: 'user' | 'assistant';
  created_at: string;
}

interface Conversation {
  id: number;
  title: string;
  text: string;
  messages: Message[];
  created_at: string;
  updated_at: string;
}

export default function ConversationPage({ params }: { params: { id: string } }) {
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [streamingText, setStreamingText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const router = useRouter();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation?.messages]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    const fetchConversation = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/learners/conversations/${params.id}/`, {
          headers: {
            Authorization: `Token ${token}`,
          },
        });

        if (res.ok) {
          const data = await res.json();
          setConversation(data);
        } else {
          setError('Failed to load conversation');
        }
      } catch (err) {
        setError('Network error');
      } finally {
        setLoading(false);
      }
    };

    fetchConversation();
  }, [params.id, router]);

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
    
    // Add the user's message immediately for better UX
    const tempUserMessage = {
      id: Date.now(),
      text: newMessage,
      role: 'user' as const,
      created_at: new Date().toISOString(),
    };
    
    setConversation(prev => {
      if (!prev) return null;
      return {
        ...prev,
        messages: [...prev.messages, tempUserMessage],
      };
    });
    
    // Clear input immediately
    setNewMessage('');

    try {
      const response = await fetch(`http://localhost:8000/api/learners/conversations/${params.id}/messages/?stream=true`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Token ${token}`,
        },
        body: JSON.stringify({ text: newMessage }),
      });

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

                setConversation(prev => {
                  if (!prev) return null;
                  return {
                    ...prev,
                    messages: [...prev.messages, aiMessage],
                  };
                });
                setIsStreaming(false);
                break;
              } else {
                accumulatedText += data.text;
                setStreamingText(accumulatedText);
              }
            } catch (e) {
              console.error('Error parsing streaming data:', e);
            }
          }
        }
      }
    } catch (err) {
      setError('Error: Failed to process the response. Please try again.');
      // Remove the temporary message if there was an error
      setConversation(prev => {
        if (!prev) return null;
        return {
          ...prev,
          messages: prev.messages.filter(m => m.id !== tempUserMessage.id),
        };
      });
    } finally {
      setSending(false);
      setIsStreaming(false);
    }
  };

  const formatMessage = (text: any): string => {
    if (typeof text === 'string') return text;
    return 'Error: Could not display message';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <ClientNavbar />
        <div className="max-w-4xl mx-auto p-4">
          <div className="text-center text-gray-600">Loading conversation...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <ClientNavbar />
        <div className="max-w-4xl mx-auto p-4">
          <div className="text-center text-red-600">{error}</div>
        </div>
      </div>
    );
  }

  if (!conversation) {
    return (
      <div className="min-h-screen bg-gray-50">
        <ClientNavbar />
        <div className="max-w-4xl mx-auto p-4">
          <div className="text-center text-gray-600">Conversation not found</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <ClientNavbar />
      <div className="max-w-4xl mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">{conversation.title}</h1>
        
        <div className="bg-white rounded-lg shadow p-4 mb-4 min-h-[400px] max-h-[600px] overflow-y-auto">
          {conversation.messages.map((message) => (
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
          ))}
          
          {isStreaming && (
            <div className="text-left mb-4">
              <div className="inline-block rounded-lg px-4 py-2 bg-gray-200 text-gray-800">
                <p className="break-words whitespace-pre-wrap typing-animation">
                  {streamingText}
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
            disabled={sending}
            className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={!newMessage.trim() || sending}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {sending ? 'Teacher is thinking...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
} 