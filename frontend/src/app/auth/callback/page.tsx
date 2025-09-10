'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

export default function AuthCallback() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { token, setToken, setUser } = useAuth();
  const [isProcessing, setIsProcessing] = useState(true);

  useEffect(() => {
    const processCallback = async () => {
      try {
        console.log('Processing OAuth callback...');
        
        // Get token from URL parameters
        const urlToken = searchParams.get('token');
        console.log('URL token:', urlToken ? 'Found' : 'Not found');
        console.log('Current context token:', token ? 'Found' : 'Not found');
        
        if (urlToken && !token) {
          console.log('Token found in URL, fetching user info...');
          
          // Token exists in URL but not in context, fetch user info
          const response = await fetch('http://localhost:8000/auth/me', {
            headers: {
              'Authorization': `Bearer ${urlToken}`,
            },
          });

          console.log('User info response status:', response.status);

          if (response.ok) {
            const userData = await response.json();
            console.log('User data received:', userData);
            
            setUser(userData);
            setToken(urlToken);
            localStorage.setItem('auth_token', urlToken);
            
            // Clean URL and redirect to dashboard
            window.history.replaceState({}, document.title, '/auth/callback');
            router.push('/');
          } else {
            // Invalid token, redirect to error
            console.error('Invalid token response:', response.status);
            router.push('/auth/error?message=Invalid token');
          }
        } else if (token) {
          // Already authenticated, redirect to dashboard
          console.log('Already authenticated, redirecting to dashboard');
          router.push('/');
        } else {
          // No token found, redirect to error
          console.error('No token found in URL or context');
          router.push('/auth/error?message=No authentication token found');
        }
      } catch (error) {
        console.error('Callback processing error:', error);
        router.push('/auth/error?message=Authentication failed');
      } finally {
        setIsProcessing(false);
      }
    };

    processCallback();
  }, [token, setToken, setUser, router, searchParams]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-gray-600">
          {isProcessing ? 'Completing authentication...' : 'Redirecting...'}
        </p>
      </div>
    </div>
  );
}
