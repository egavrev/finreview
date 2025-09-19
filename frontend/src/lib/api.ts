// API Configuration
// This file handles the API base URL configuration for different environments

// Get API base URL from environment variable or fallback to localhost
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
export const API_BASE_URL = 'https://finreview-app-rq7lgavxwq-ew.a.run.app';

// Helper function to build API URLs
export const buildApiUrl = (endpoint: string): string => {
  // Remove leading slash if present
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  return `${API_BASE_URL}/${cleanEndpoint}`;
};

// Common API endpoints
export const API_ENDPOINTS = {
  // PDF endpoints
  PDFS: buildApiUrl('pdfs'),
  PDF_BY_ID: (id: number) => buildApiUrl(`pdfs/${id}`),
  DELETE_PDF: (id: number) => buildApiUrl(`pdfs/${id}`),
  UPLOAD_PDF: buildApiUrl('upload-pdf'),
  
  // Operations endpoints
  OPERATIONS: buildApiUrl('operations'),
  OPERATIONS_NULL_TYPES: buildApiUrl('operations/null-types'),
  OPERATIONS_WITH_TYPES: buildApiUrl('operations/with-types'),
  OPERATIONS_BY_TYPE: (typeId: number) => buildApiUrl(`operations/by-type/${typeId}`),
  OPERATIONS_BY_MONTH: (year: number, month: number) => buildApiUrl(`operations/by-month/${year}/${month}`),
  ASSIGN_OPERATION_TYPE: (operationId: number) => buildApiUrl(`operations/${operationId}/assign-type`),
  DELETE_OPERATION: (operationId: number) => buildApiUrl(`operations/${operationId}`),
  CREATE_MANUAL_OPERATION: buildApiUrl('operations/manual'),
  
  // Operation types endpoints
  OPERATION_TYPES: buildApiUrl('operation-types'),
  OPERATION_TYPE_BY_ID: (typeId: number) => buildApiUrl(`operation-types/${typeId}`),
  
  // Reports endpoints
  AVAILABLE_MONTHS: buildApiUrl('reports/available-months'),
  MONTHLY_REPORT: (year: number, month: number) => buildApiUrl(`reports/monthly/${year}/${month}`),
  MONTHLY_OPERATIONS_BY_TYPE: (year: number, month: number, typeId: number) => 
    buildApiUrl(`reports/monthly/${year}/${month}/type/${typeId}`),
  
  // Statistics
  STATISTICS: buildApiUrl('statistics'),
  
  // Rules management endpoints
  RULES: {
    CATEGORIES: `${API_BASE_URL}/api/rules/categories`,
    CATEGORY_BY_ID: (id: number) => `${API_BASE_URL}/api/rules/categories/${id}`,
    RULES: `${API_BASE_URL}/api/rules/rules`,
    RULE_BY_ID: (id: number) => `${API_BASE_URL}/api/rules/rules/${id}`,
    RULE_TEST: (id: number) => `${API_BASE_URL}/api/rules/rules/${id}/test`,
    RULE_VALIDATE: `${API_BASE_URL}/api/rules/rules/validate`,
    RULE_STATS: (id: number) => `${API_BASE_URL}/api/rules/rules/${id}/statistics`,
    CATEGORY_STATS: (name: string) => `${API_BASE_URL}/api/rules/categories/${name}/statistics`,
    BULK_PRIORITY: `${API_BASE_URL}/api/rules/rules/bulk-priority`,
    RUN_MATCHER: `${API_BASE_URL}/api/rules/run-matcher`,
  },
};
