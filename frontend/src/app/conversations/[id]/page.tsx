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
  const [visibleChars, setVisibleChars] = useState(0);
  const [shouldStop, setShouldStop] = useState(false);
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  const router = useRouter();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const refreshConversation = async () => {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/learners/conversations/${params.id}/`, {
        headers: {
          Authorization: `Token ${token}`,
        },
      });

      if (res.ok) {
        const data = await res.json();
        setConversation(data);
      }
    } catch (err) {
      console.error('Failed to refresh conversation:', err);
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation?.messages, streamingText]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    const fetchConversation = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/learners/conversations/${params.id}/`, {
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

  const handleStop = () => {
    // Set stop flag immediately
    setShouldStop(true);
    
    // Abort the request immediately
    if (abortController) {
      abortController.abort();
    }
    
    // Immediately save the partial response to the conversation
    if (streamingText.trim()) {
      const aiMessage = {
        id: Date.now(),
        text: streamingText + ' [Response stopped by user]',
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
    }
    
    // Clear streaming state immediately
    setIsStreaming(false);
    setStreamingText('');
    setVisibleChars(0);
    setSending(false);
    
    // Refresh conversation from database to ensure consistency
    setTimeout(() => {
      refreshConversation();
    }, 100);
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
    setShouldStop(false);
    
    // Create abort controller for this request
    const controller = new AbortController();
    setAbortController(controller);
    
    // Store the message text and clear input immediately
    const messageText = newMessage;
    setNewMessage('');
    
    // Add the user's message immediately for better UX
    const tempUserMessage = {
      id: Date.now(),
      text: messageText,
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

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/learners/conversations/${params.id}/messages/?stream=true`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Token ${token}`,
        },
        body: JSON.stringify({ text: messageText }),
        signal: controller.signal,
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
        // Check if user wants to stop - do this at the beginning of each iteration
        if (shouldStop) {
          reader.cancel();
          break;
        }

        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }

        // Convert the chunk to text
        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          // Check for stop again before processing each line
          if (shouldStop) {
            reader.cancel();
            break;
          }
          
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(5));
              if (data.done) {
                // Check if the accumulated text is an error message
                const isErrorMessage = accumulatedText.includes('I apologize') && 
                                     (accumulatedText.includes('unavailable') || 
                                      accumulatedText.includes('error') || 
                                      accumulatedText.includes('failed') ||
                                      accumulatedText.includes('busy') ||
                                      accumulatedText.includes('timeout'));
                
                if (isErrorMessage) {
                  // Remove the user message and show error
                  setConversation(prev => {
                    if (!prev) return null;
                    return {
                      ...prev,
                      messages: prev.messages.filter(m => m.id !== tempUserMessage.id),
                    };
                  });
                  setError(accumulatedText);
                } else {
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
                }
                setIsStreaming(false);
                break;
              } else {
                // Check for stop before adding text
                if (shouldStop) {
                  reader.cancel();
                  break;
                }
                
                accumulatedText += data.text;
                setStreamingText(accumulatedText);
                setVisibleChars(prev => prev + 1);
                
                // Add a small delay for realistic typing speed
                await new Promise(resolve => setTimeout(resolve, 30));
              }
            } catch (e) {
              console.error('Error parsing streaming data:', e);
            }
          }
        }
        
        // Check for stop after processing all lines in the chunk
        if (shouldStop) {
          reader.cancel();
          break;
        }
      }

      // If stopped by user, save the partial response
      if (shouldStop && accumulatedText.trim()) {
        // This is now handled in handleStop function
        // No need to duplicate the logic here
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        // Request was aborted, this is expected when stopping
        console.log('Request aborted by user');
      } else {
        setError('Error: Failed to process the response. Please try again.');
        // Remove the temporary message if there was an error
        setConversation(prev => {
          if (!prev) return null;
          return {
            ...prev,
            messages: prev.messages.filter(m => m.id !== tempUserMessage.id),
          };
        });
      }
    } finally {
      setSending(false);
      setIsStreaming(false);
      setShouldStop(false);
      setAbortController(null);
      
      // Refresh conversation from database to ensure consistency
      setTimeout(() => {
        refreshConversation();
      }, 100);
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
              <div className="inline-block rounded-lg px-4 py-2 bg-gray-200 text-gray-800 border-2 border-blue-300 max-w-[70%]">
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
            disabled={sending && !shouldStop}
            className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
          {isStreaming ? (
            <button
              type="button"
              onClick={handleStop}
              className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            >
              Stop
            </button>
          ) : (
            <button
              type="submit"
              disabled={!newMessage.trim() || sending}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {sending ? 'Teacher is thinking...' : 'Send'}
            </button>
          )}
        </form>
      </div>
    </div>
  );
} 