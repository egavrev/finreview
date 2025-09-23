'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { buildApiUrl } from '@/lib/api';

export default function AuthCallback() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { token, setToken, setUser } = useAuth();
  const [isProcessing, setIsProcessing] = useState(true);
  
  // Debug flag: enable via ?debug=1 or localStorage.setItem('finreview_debug','1')
  const isDebugEnabled = (() => {
    if (typeof window === 'undefined') return false;
    try {
      const urlHasDebug = new URLSearchParams(window.location.search).has('debug');
      const lsDebug = localStorage.getItem('finreview_debug') === '1';
      return urlHasDebug || lsDebug;
    } catch {
      return false;
    }
  })();

  useEffect(() => {
    const processCallback = async () => {
      try {
        if (isDebugEnabled && typeof window !== 'undefined') {
          // eslint-disable-next-line no-console
          console.log('[Callback] Processing OAuth callback. href:', window.location.href);
        }
        
        // Get token from URL parameters
        const urlToken = searchParams.get('token');
        if (isDebugEnabled) {
          // eslint-disable-next-line no-console
          console.log('[Callback] URL token present:', Boolean(urlToken), 'Context token present:', Boolean(token));
        }
        
        if (urlToken && !token) {
          if (isDebugEnabled) {
            // eslint-disable-next-line no-console
            console.log('[Callback] Token in URL. Fetching user info via auth/me...');
          }
          
          // Token exists in URL but not in context, fetch user info
          const response = await fetch(buildApiUrl('auth/me'), {
            headers: {
              'Authorization': `Bearer ${urlToken}`,
            },
          });

          if (isDebugEnabled) {
            // eslint-disable-next-line no-console
            console.log('[Callback] auth/me status:', response.status);
          }

          if (response.ok) {
            const userData = await response.json();
            if (isDebugEnabled) {
              // eslint-disable-next-line no-console
              console.log('[Callback] User data:', userData);
            }
            
            setUser(userData);
            setToken(urlToken);
            localStorage.setItem('auth_token', urlToken);
            
            // Clean URL and redirect to dashboard
            window.history.replaceState({}, document.title, '/auth/callback');
            router.push('/');
          } else {
            // Invalid token, redirect to error
            if (isDebugEnabled) {
              const body = await response.text().catch(() => '<no body>');
              // eslint-disable-next-line no-console
              console.error('[Callback] auth/me failed. Status:', response.status, 'Body:', body);
            }
            router.push('/auth/error?message=Invalid token');
          }
        } else if (token) {
          // Already authenticated, redirect to dashboard
          if (isDebugEnabled) {
            // eslint-disable-next-line no-console
            console.log('[Callback] Context already has token. Redirecting to /.');
          }
          router.push('/');
        } else {
          // No token found, redirect to error
          if (isDebugEnabled) {
            // eslint-disable-next-line no-console
            console.error('[Callback] No token found in URL or context.');
          }
          router.push('/auth/error?message=No authentication token found');
        }
      } catch (error) {
        if (isDebugEnabled) {
          // eslint-disable-next-line no-console
          console.error('[Callback] Processing error:', error);
        }
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
