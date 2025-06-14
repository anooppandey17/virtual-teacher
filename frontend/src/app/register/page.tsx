'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';

type UserRole = 'LEARNER' | 'TEACHER' | 'PARENT' | 'ADMIN';

export default function SignupPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password1, setPassword1] = useState('');
  const [password2, setPassword2] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [role, setRole] = useState<UserRole>('LEARNER');
  const [gender, setGender] = useState('M');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [grade, setGrade] = useState('1');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [usernameError, setUsernameError] = useState('');
  const [checkingUsername, setCheckingUsername] = useState(false);
  const router = useRouter();

  // Redirect if already logged in
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      router.push('/learner');
    }
  }, [router]);

  // Debounced username validation
  const checkUsername = useCallback(async (username: string) => {
    if (!username) {
      setUsernameError('');
      return;
    }

    setCheckingUsername(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/check-username/?username=${encodeURIComponent(username)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await res.json();
      if (!res.ok) {
        setUsernameError(data.detail || 'Username is already taken');
      } else {
        setUsernameError('');
      }
    } catch (err) {
      console.error('Error checking username:', err);
    } finally {
      setCheckingUsername(false);
    }
  }, []);

  // Debounce username check
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (username.length >= 3) {
        checkUsername(username);
      }
    }, 500); // Wait 500ms after user stops typing

    return () => clearTimeout(timeoutId);
  }, [username, checkUsername]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');

    // Validate before submission
    if (usernameError) {
      setError('Please fix the username issues before submitting');
      return;
    }

    if (password1 !== password2) {
      setError("Passwords don't match");
      return;
    }

    // Validate grade for learners
    if (role === 'LEARNER' && !grade) {
      setError('Grade is required for learners');
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/registration/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          email,
          password1,
          password2,
          first_name: firstName,
          last_name: lastName,
          role,
          gender,
          phone_number: phoneNumber,
          ...(role === 'LEARNER' ? { grade } : {})
        }),
      });

      const data = await res.json();

      if (res.ok) {
        localStorage.setItem('token', data.key);
        router.push('/learner');
      } else {
        // Handle different types of errors
        if (data.non_field_errors) {
          setError(data.non_field_errors.join(' '));
        } else if (data.password1) {
          setError(data.password1.join(' '));
        } else if (typeof data === 'object') {
          const errorMessages = Object.entries(data)
            .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(' ') : value}`)
            .join('. ');
          setError(errorMessages);
        } else {
          setError(data.detail || JSON.stringify(data));
        }
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-full flex items-center justify-center bg-gradient-to-br from-blue-50 to-white px-4">
      <div className="w-full max-w-xl bg-white rounded-lg shadow-lg p-4 border border-pink-200">
        <h1 className="text-2xl font-bold text-blue-600 mb-2 text-center">Create Account</h1>
        
        {/* Password Requirements Notice */}
        <div className="bg-blue-50 p-3 rounded-lg mb-4 text-sm text-blue-600">
          <h2 className="font-bold mb-1">Password Requirements:</h2>
          <ul className="list-disc list-inside space-y-1">
            <li>At least 8 characters long</li>
            <li>Must not be too similar to your username or email</li>
            <li>Must not be a commonly used password</li>
            <li>Must contain at least one number and one letter</li>
          </ul>
        </div>

        {error && <p className="text-red-500 text-xl text-center">{error}</p>}

        <form onSubmit={handleSubmit} className="space-y-2">
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label htmlFor="firstName" className="block text-lg font-medium font-bold text-blue-600">
                First Name
              </label>
              <input
                id="firstName"
                type="text"
                placeholder="Enter first name"
                value={firstName}
                onChange={e => setFirstName(e.target.value)}
                required
                className="w-full px-2 py-1 text-lg border border-gray-300 rounded focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-200 text-gray-800 placeholder-gray-400"
              />
            </div>
            <div>
              <label htmlFor="lastName" className="block text-lg font-medium font-bold text-blue-600">
                Last Name
              </label>
              <input
                id="lastName"
                type="text"
                placeholder="Enter last name"
                value={lastName}
                onChange={e => setLastName(e.target.value)}
                required
                className="w-full px-2 py-1 text-lg border border-gray-300 rounded focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-200 text-gray-800 placeholder-gray-400"
              />
            </div>
          </div>

          <div>
            <label htmlFor="username" className="block text-lg font-medium font-bold text-blue-600">
              Username
            </label>
            <input
              id="username"
              type="text"
              placeholder="Choose a username"
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
              className={`w-full px-2 py-1 text-lg border ${
                username.length >= 3
                  ? usernameError
                    ? 'border-red-500'
                    : 'border-green-500'
                  : 'border-gray-300'
              } rounded focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-200 text-gray-800 placeholder-gray-400`}
            />
            {checkingUsername && (
              <p className="text-gray-500 text-sm mt-1">Checking username availability...</p>
            )}
            {!checkingUsername && username.length >= 3 && (
              usernameError ? (
                <p className="text-red-500 text-sm mt-1">{usernameError}</p>
              ) : (
                <p className="text-green-500 text-sm mt-1">Username is available!</p>
              )
            )}
          </div>

          <div>
            <label htmlFor="email" className="block text-lg font-medium font-bold text-blue-600">
              Email
            </label>
            <input
              id="email"
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              className="w-full px-2 py-1 text-lg border border-gray-300 rounded focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-200 text-gray-800 placeholder-gray-400"
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label htmlFor="role" className="block text-lg font-medium font-bold text-blue-600">
                Role
              </label>
              <select
                id="role"
                value={role}
                onChange={e => setRole(e.target.value as UserRole)}
                required
                className="w-full px-2 py-1 text-lg border border-gray-300 rounded focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-200 text-gray-800"
              >
                <option value="LEARNER">Learner</option>
                <option value="TEACHER">Teacher</option>
                <option value="PARENT">Parent</option>
              </select>
            </div>
            <div>
              <label htmlFor="gender" className="block text-lg font-medium font-bold text-blue-600">
                Gender
              </label>
              <select
                id="gender"
                value={gender}
                onChange={e => setGender(e.target.value)}
                required
                className="w-full px-2 py-1 text-lg border border-gray-300 rounded focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-200 text-gray-800"
              >
                <option value="M">Male</option>
                <option value="F">Female</option>
                <option value="O">Other</option>
              </select>
            </div>
          </div>

          {/* Grade Selection - Only show for Learner role */}
          {role === 'LEARNER' && (
            <div>
              <label htmlFor="grade" className="block text-lg font-medium font-bold text-blue-600">
                Grade
              </label>
              <select
                id="grade"
                value={grade}
                onChange={e => setGrade(e.target.value)}
                required
                className="w-full px-2 py-1 text-lg border border-gray-300 rounded focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-200 text-gray-800"
              >
                <option value="4">Grade 4</option>
                <option value="5">Grade 5</option>
                <option value="6">Grade 6</option>
                <option value="7">Grade 7</option>
                <option value="8">Grade 8</option>
                <option value="9">Grade 9</option>
                <option value="10">Grade 10</option>
                <option value="11">Grade 11</option>
                <option value="12">Grade 12</option>
              </select>
            </div>
          )}

          <div>
            <label htmlFor="phoneNumber" className="block text-lg font-medium font-bold text-blue-600">
              Phone Number
            </label>
            <input
              id="phoneNumber"
              type="tel"
              placeholder="Enter phone number"
              value={phoneNumber}
              onChange={e => setPhoneNumber(e.target.value)}
              required
              className="w-full px-2 py-1 text-lg border border-gray-300 rounded focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-200 text-gray-800 placeholder-gray-400"
            />
          </div>

          <div>
            <label htmlFor="password1" className="block text-lg font-medium font-bold text-blue-600">
              Password
            </label>
            <input
              id="password1"
              type="password"
              placeholder="Create a password"
              value={password1}
              onChange={e => setPassword1(e.target.value)}
              required
              minLength={8}
              className="w-full px-2 py-1 text-lg border border-gray-300 rounded focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-200 text-gray-800 placeholder-gray-400"
            />
          </div>

          <div>
            <label htmlFor="password2" className="block text-lg font-medium font-bold text-blue-600">
              Confirm Password
            </label>
            <input
              id="password2"
              type="password"
              placeholder="Confirm your password"
              value={password2}
              onChange={e => setPassword2(e.target.value)}
              required
              minLength={8}
              className="w-full px-2 py-1 text-lg border border-gray-300 rounded focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-200 text-gray-800 placeholder-gray-400"
            />
          </div>

          <button
            type="submit"
            disabled={loading || !!usernameError}
            className="w-full bg-blue-600 text-white py-1 rounded text-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-1 focus:ring-blue-400 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed mt-1"
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>
      </div>
    </div>
  );
} 