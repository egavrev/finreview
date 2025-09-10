'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';

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

  // Check if user is authenticated
  const isAuthenticated = !!user && !!token;

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedToken = localStorage.getItem('auth_token');
        if (storedToken) {
          setToken(storedToken);
          // Verify token by fetching user info
          const response = await fetch('http://localhost:8000/auth/me', {
            headers: {
              'Authorization': `Bearer ${storedToken}`,
            },
          });

          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
          } else {
            // Token is invalid, remove it
            localStorage.removeItem('auth_token');
            setToken(null);
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
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
      // Get the OAuth URL from the backend
      const response = await fetch('http://localhost:8000/auth/google');
      const data = await response.json();
      
      if (data.auth_url) {
        // Redirect to the Google OAuth URL
        window.location.href = data.auth_url;
      } else {
        console.error('No auth_url received from backend');
        alert('Authentication failed. Please try again.');
      }
    } catch (error) {
      console.error('Error getting OAuth URL:', error);
      alert('Authentication failed. Please try again.');
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('auth_token');
    
    // Call logout endpoint
    fetch('http://localhost:8000/auth/logout', {
      method: 'POST',
    }).catch(console.error);
  };

  // Handle OAuth callback from URL fragment
  useEffect(() => {
    const handleOAuthCallback = () => {
      // Check if we're on the callback page and have a token in the URL fragment
      if (window.location.pathname === '/auth/callback') {
        const hash = window.location.hash;
        if (hash && hash.startsWith('#')) {
          const token = hash.substring(1); // Remove the # symbol
          
          if (token) {
            setIsLoading(true);
            
            // Store the token and fetch user info
            setToken(token);
            localStorage.setItem('auth_token', token);
            
            // Fetch user info to complete authentication
            fetch('http://localhost:8000/auth/me', {
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            })
            .then(response => {
              if (response.ok) {
                return response.json();
              } else {
                throw new Error('Failed to fetch user info');
              }
            })
            .then(userData => {
              setUser(userData);
              // Redirect to dashboard
              window.history.replaceState({}, document.title, '/');
              window.location.href = '/';
            })
            .catch(error => {
              console.error('Error fetching user info:', error);
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
