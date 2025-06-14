'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function RootPage() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    const checkAuthAndRedirect = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/me/`, {
          headers: {
            Authorization: `Token ${token}`,
          },
        });

        if (res.ok) {
          const user = await res.json();
          // Redirect based on user role
          switch (user.role) {
            case 'LEARNER':
              router.push('/learner');
              break;
            case 'TEACHER':
              router.push('/teacher');
              break;
            case 'PARENT':
              router.push('/parent');
              break;
            case 'ADMIN':
              router.push('/admin');
              break;
            default:
              router.push('/login');
          }
        } else {
          localStorage.removeItem('token');
          router.push('/login');
        }
      } catch (err) {
        console.error('Error checking auth:', err);
        localStorage.removeItem('token');
        router.push('/login');
      }
    };

    checkAuthAndRedirect();
  }, [router]);

  // Show a loading state while checking auth
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="text-2xl font-semibold text-gray-700 mb-2">Virtual Teacher</div>
        <div className="text-gray-500">Loading...</div>
      </div>
    </div>
  );
} 