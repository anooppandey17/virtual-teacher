'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import ClientNavbar from '../components/ClientNavbar';

interface Conversation {
  id: number;
  title: string;
  text: string;
  last_message: string;
  created_at: string;
  updated_at: string;
}

interface GroupedConversations {
  today: Conversation[];
  thisWeek: Conversation[];
  older: Conversation[];
}

export default function LearnerDashboard() {
  const [conversations, setConversations] = useState<GroupedConversations>({
    today: [],
    thisWeek: [],
    older: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  const groupConversations = (convs: Conversation[]) => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const thisWeek = new Date(today);
    thisWeek.setDate(today.getDate() - 7);

    return convs.reduce(
      (groups: GroupedConversations, conv) => {
        const convDate = new Date(conv.updated_at);
        if (convDate >= today) {
          groups.today.push(conv);
        } else if (convDate >= thisWeek) {
          groups.thisWeek.push(conv);
        } else {
          groups.older.push(conv);
        }
        return groups;
      },
      { today: [], thisWeek: [], older: [] }
    );
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    const fetchConversations = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/learners/conversations/', {
          headers: {
            Authorization: `Token ${token}`,
          },
        });

        if (res.ok) {
          const data = await res.json();
          setConversations(groupConversations(data));
        } else {
          setError('Failed to load conversations');
        }
      } catch (err) {
        setError('Network error');
      } finally {
        setLoading(false);
      }
    };

    fetchConversations();
  }, [router]);

  const createNewConversation = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const res = await fetch('http://localhost:8000/api/learners/conversations/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Token ${token}`,
        },
        body: JSON.stringify({ prompt: "" }),  // <-- Explicitly send empty prompt
      });

      if (res.ok) {
        const conversation = await res.json();
        router.push(`/conversations/${conversation.id}`);
      } else {
        setError('Failed to create conversation');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  const ConversationGroup = ({ title, items, emptyMessage }: { title: string; items: Conversation[]; emptyMessage?: string }) => (
    <div className="mb-8">
      <h2 className="text-xl font-bold text-gray-800 mb-4">{title}</h2>
      {items.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {items.map((conversation) => (
            <Link
              key={conversation.id}
              href={`/conversations/${conversation.id}`}
              className="block bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-200"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {conversation.title}
              </h3>
              {conversation.last_message && (
                <p className="text-gray-600 text-sm mb-2 line-clamp-2">
                  {conversation.last_message}
                </p>
              )}
              <p className="text-gray-400 text-xs">
                {new Date(conversation.updated_at).toLocaleTimeString([], { 
                  hour: '2-digit', 
                  minute: '2-digit',
                  hour12: true 
                })}
              </p>
            </Link>
          ))}
        </div>
      ) : emptyMessage ? (
        <p className="text-gray-500 text-center py-4">{emptyMessage}</p>
      ) : null}
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <ClientNavbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-600">Loading conversations...</div>
        </div>
      </div>
    );
  }

  const hasNoConversations = 
    conversations.today.length === 0 && 
    conversations.thisWeek.length === 0 && 
    conversations.older.length === 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <ClientNavbar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Your Learning Journey</h1>
          <button
            onClick={createNewConversation}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            New Conversation
          </button>
        </div>

        {error && (
          <div className="bg-red-50 text-red-500 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {hasNoConversations ? (
          <div className="text-center text-gray-600 mt-8">
            <p className="mb-4">You haven't started any conversations yet.</p>
            <button
              onClick={createNewConversation}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Start your first conversation
            </button>
          </div>
        ) : (
          <div>
            <ConversationGroup 
              title="Today's Learning 📚" 
              items={conversations.today}
              emptyMessage="No conversations today yet"
            />
            <ConversationGroup 
              title="This Week's Progress 🎯" 
              items={conversations.thisWeek}
              emptyMessage="No conversations this week"
            />
            <ConversationGroup 
              title="Previous Learning 📅" 
              items={conversations.older}
              emptyMessage="No previous conversations"
            />
          </div>
        )}
      </div>
    </div>
  );
}
