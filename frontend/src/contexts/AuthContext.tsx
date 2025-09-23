'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { buildApiUrl } from '@/lib/api';

interface User {
  id: number;
  email: string;
  name: string;
  picture?: string;
  created_at: string;
  last_login?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: () => void;
  logout: () => void;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // Debug flag: enable by adding ?debug=1 to URL or localStorage.setItem('finreview_debug','1')
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

  // Check if user is authenticated
  const isAuthenticated = !!user && !!token;

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedToken = localStorage.getItem('auth_token');
        if (isDebugEnabled) {
          // Lazy import to avoid cycle; duplicate builder kept minimal
          const { buildApiUrl } = await import('@/lib/api');
          // eslint-disable-next-line no-console
          console.log('[AuthInit] Start. Stored token present:', Boolean(storedToken), 'auth/me URL:', buildApiUrl('auth/me'));
        }
        if (storedToken) {
          setToken(storedToken);
          // Verify token by fetching user info
          const response = await fetch(buildApiUrl('auth/me'), {
            headers: {
              'Authorization': `Bearer ${storedToken}`,
            },
          });

          if (response.ok) {
            const userData = await response.json();
            if (isDebugEnabled) {
              // eslint-disable-next-line no-console
              console.log('[AuthInit] /auth/me success. User:', userData);
            }
            setUser(userData);
          } else {
            // Token is invalid, remove it
            if (isDebugEnabled) {
              const raw = await response.text().catch(() => '<no body>');
              // eslint-disable-next-line no-console
              console.error('[AuthInit] /auth/me failed. Status:', response.status, 'Body:', raw);
            }
            localStorage.removeItem('auth_token');
            setToken(null);
          }
        }
      } catch (error) {
        if (isDebugEnabled) {
          // eslint-disable-next-line no-console
          console.error('[AuthInit] Error:', error);
        }
        localStorage.removeItem('auth_token');
        setToken(null);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async () => {
    try {
      if (isDebugEnabled) {
        // eslint-disable-next-line no-console
        console.log('[Auth] Requesting OAuth URL...');
      }
      // Get the OAuth URL from the backend
      const response = await fetch(buildApiUrl('auth/google'));
      if (isDebugEnabled) {
        // eslint-disable-next-line no-console
        console.log('[Auth] /auth/google status:', response.status);
      }
      const data = await response.json().catch(() => null);
      if (isDebugEnabled) {
        // eslint-disable-next-line no-console
        console.log('[Auth] /auth/google body:', data);
      }
      
      if (data.auth_url) {
        // Redirect to the Google OAuth URL
        if (isDebugEnabled) {
          // eslint-disable-next-line no-console
          console.log('[Auth] Redirecting to Google auth_url:', data.auth_url);
        }
        window.location.href = data.auth_url;
      } else {
        console.error('No auth_url received from backend');
        alert('Authentication failed. Please try again.');
      }
    } catch (error) {
      if (isDebugEnabled) {
        // eslint-disable-next-line no-console
        console.error('[Auth] Error getting OAuth URL:', error);
      }
      alert('Authentication failed. Please try again.');
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('auth_token');
    
    // Call logout endpoint
    fetch(buildApiUrl('auth/logout'), {
      method: 'POST',
    }).catch(console.error);
  };

  // Handle OAuth callback from URL fragment
  useEffect(() => {
    const handleOAuthCallback = () => {
      // Check if we're on the callback page and have a token in the URL fragment
      if (window.location.pathname === '/auth/callback') {
        const hash = window.location.hash;
        if (isDebugEnabled) {
          // eslint-disable-next-line no-console
          console.log('[CallbackLegacy] location.href:', window.location.href, 'hash:', hash);
        }
        if (hash && hash.startsWith('#')) {
          const token = hash.substring(1); // Remove the # symbol
          
          if (token) {
            setIsLoading(true);
            
            // Store the token and fetch user info
            setToken(token);
            localStorage.setItem('auth_token', token);
            
            // Fetch user info to complete authentication
            fetch(buildApiUrl('auth/me'), {
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            })
            .then(response => {
              if (response.ok) {
                return response.json();
              } else {
                if (isDebugEnabled) {
                  // eslint-disable-next-line no-console
                  console.error('[CallbackLegacy] /auth/me failed. Status:', response.status);
                }
                throw new Error('Failed to fetch user info');
              }
            })
            .then(userData => {
              if (isDebugEnabled) {
                // eslint-disable-next-line no-console
                console.log('[CallbackLegacy] /auth/me success. User:', userData);
              }
              setUser(userData);
              // Redirect to dashboard
              window.history.replaceState({}, document.title, '/');
              window.location.href = '/';
            })
            .catch(error => {
              if (isDebugEnabled) {
                // eslint-disable-next-line no-console
                console.error('[CallbackLegacy] Error fetching user info:', error);
              }
              // Clear invalid token
              setToken(null);
              localStorage.removeItem('auth_token');
              alert('Authentication failed. Please try again.');
            })
            .finally(() => {
              setIsLoading(false);
            });
          }
        }
      }
    };

    handleOAuthCallback();
  }, []);

  const value: AuthContextType = {
    user,
    token,
    isLoading,
    login,
    logout,
    isAuthenticated,
    setUser,
    setToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
