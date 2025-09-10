'use client';

import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export const UserProfile: React.FC = () => {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="flex items-center gap-3">
          {user.picture && (
            <img
              src={user.picture}
              alt={user.name}
              className="w-10 h-10 rounded-full"
            />
          )}
          <div>
            <h3 className="text-lg font-semibold">{user.name}</h3>
            <p className="text-sm text-gray-600">{user.email}</p>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2 text-sm text-gray-600">
          <p><strong>Account created:</strong> {new Date(user.created_at).toLocaleDateString()}</p>
          {user.last_login && (
            <p><strong>Last login:</strong> {new Date(user.last_login).toLocaleDateString()}</p>
          )}
        </div>
        <Button 
          onClick={logout} 
          variant="outline" 
          className="w-full mt-4"
        >
          Sign Out
        </Button>
      </CardContent>
    </Card>
  );
};
