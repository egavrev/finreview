import React, { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'

// Create a custom render function that includes basic providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return <>{children}</>
}

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options })

// Mock data for testing
export const mockOperations = [
  {
    id: 1,
    date: '2024-01-15',
    description: 'Grocery Store Purchase',
    amount: -85.50,
    type: 'Food & Dining',
    category: 'Groceries',
    account: 'Checking Account',
  },
  {
    id: 2,
    date: '2024-01-16',
    description: 'Salary Deposit',
    amount: 2500.00,
    type: 'Income',
    category: 'Salary',
    account: 'Checking Account',
  },
  {
    id: 3,
    date: '2024-01-17',
    description: 'Gas Station',
    amount: -45.00,
    type: 'Transportation',
    category: 'Fuel',
    account: 'Credit Card',
  },
]

export const mockPdfFiles = [
  {
    id: 1,
    filename: 'bank_statement_jan_2024.pdf',
    uploadDate: '2024-01-20T10:30:00Z',
    status: 'processed',
    totalOperations: 45,
    totalAmount: 1250.75,
  },
  {
    id: 2,
    filename: 'credit_card_statement_jan_2024.pdf',
    uploadDate: '2024-01-21T14:15:00Z',
    status: 'processing',
    totalOperations: 23,
    totalAmount: -890.25,
  },
]

export const mockReports = [
  {
    id: 1,
    title: 'January 2024 Financial Summary',
    period: '2024-01',
    generatedDate: '2024-01-31T23:59:59Z',
    totalIncome: 3500.00,
    totalExpenses: 2150.75,
    netAmount: 1349.25,
    categories: [
      { name: 'Food & Dining', amount: 450.00, percentage: 20.9 },
      { name: 'Transportation', amount: 180.00, percentage: 8.4 },
      { name: 'Entertainment', amount: 120.00, percentage: 5.6 },
    ],
  },
]

// Mock API responses
export const mockApiResponses = {
  operations: {
    list: mockOperations,
    create: { success: true, id: 4 },
    update: { success: true },
    delete: { success: true },
  },
  pdfFiles: {
    list: mockPdfFiles,
    upload: { success: true, id: 3 },
    process: { success: true, status: 'processing' },
  },
  reports: {
    list: mockReports,
    generate: { success: true, id: 2 },
  },
}

// Helper function to create mock functions
export const createMockFunction = <T extends (...args: any[]) => any>(
  implementation?: T
) => {
  return jest.fn(implementation)
}

// Helper function to wait for async operations
export const waitFor = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// Helper function to mock fetch
export const mockFetch = (response: any, status = 200) => {
  return jest.fn().mockResolvedValue({
    ok: status < 400,
    status,
    json: async () => response,
    text: async () => JSON.stringify(response),
  })
}

// Re-export everything from testing library
export * from '@testing-library/react'
export { customRender as render }
