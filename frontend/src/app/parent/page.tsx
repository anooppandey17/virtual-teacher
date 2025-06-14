'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import ClientNavbar from '../components/ClientNavbar';

interface Child {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  grade: string;
  last_active: string;
  total_conversations: number;
  recent_subjects: string[];
}

export default function ParentDashboard() {
  const [children, setChildren] = useState<Child[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    const fetchChildren = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/parent/children/`, {
          headers: {
            Authorization: `Token ${token}`,
          },
        });

        if (res.ok) {
          const data = await res.json();
          setChildren(data);
        } else {
          setError('Failed to load children');
        }
      } catch (err) {
        setError('Network error');
      } finally {
        setLoading(false);
      }
    };

    fetchChildren();
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <ClientNavbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-600">Loading children's data...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <ClientNavbar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Your Children's Progress</h1>
        </div>

        {error && (
          <div className="bg-red-50 text-red-500 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {children.map((child) => (
            <div
              key={child.id}
              className="bg-white rounded-lg shadow-sm p-6 border border-gray-200"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">
                    {child.first_name} {child.last_name}
                  </h2>
                  <p className="text-sm text-gray-500">Grade {child.grade}</p>
                </div>
                <Link
                  href={`/parent/children/${child.id}`}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  View Details
                </Link>
              </div>

              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">Total Conversations</p>
                  <p className="text-lg font-medium text-gray-900">
                    {child.total_conversations}
                  </p>
                </div>

                <div>
                  <p className="text-sm text-gray-600">Recent Subjects</p>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {child.recent_subjects.map((subject, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                      >
                        {subject}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="text-sm text-gray-600">Last Active</p>
                  <p className="text-gray-900">
                    {new Date(child.last_active).toLocaleDateString()}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {children.length === 0 && !error && (
          <div className="text-center text-gray-600 mt-8">
            <p>No children found. Please contact support if you believe this is an error.</p>
          </div>
        )}
      </div>
    </div>
  );
} 