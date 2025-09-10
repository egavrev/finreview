'use client';

import React from 'react';
import RulesManagement from '@/components/rules-management';
import { ProtectedRoute } from '@/components/ProtectedRoute';

export default function RulesPage() {
  return (
    <ProtectedRoute>
      <div className="container mx-auto py-6 px-4">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Rules Management</h1>
        <p className="text-gray-600 mt-2">
          Manage operation matching rules and categories for automatic classification
        </p>
      </div>
      
      <RulesManagement />
      </div>
    </ProtectedRoute>
  );
}
