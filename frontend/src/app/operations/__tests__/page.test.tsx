import React from 'react'
import { render, screen, fireEvent, waitFor } from '../../../lib/test-utils'
import OperationsPage from '../page'

// Mock fetch globally
const mockFetch = jest.fn()
global.fetch = mockFetch

describe('OperationsPage Component', () => {
  const mockOperations = [
    {
      id: 1,
      pdf_id: 1,
      type_id: null,
      type_name: null,
      transaction_date: '2024-01-15T10:30:00Z',
      processed_date: '2024-01-15T10:35:00Z',
      description: 'Test operation 1',
      amount_lei: 150.50,
      is_manual: false
    },
    {
      id: 2,
      pdf_id: 1,
      type_id: null,
      type_name: null,
      transaction_date: '2024-01-15T11:00:00Z',
      processed_date: '2024-01-15T11:05:00Z',
      description: 'Test operation 2',
      amount_lei: 250.75,
      is_manual: false
    }
  ]

  const mockOperationTypes = [
    {
      id: 1,
      name: 'Groceries',
      description: 'Food and household items',
      created_at: '2024-01-01T00:00:00Z'
    },
    {
      id: 2,
      name: 'Transport',
      description: 'Transportation expenses',
      created_at: '2024-01-01T00:00:00Z'
    }
  ]

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should render operations table when data is loaded', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockOperations
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockOperationTypes
      })

    render(<OperationsPage />)
    
    await waitFor(() => {
      expect(screen.getByText('Test operation 1')).toBeInTheDocument()
      expect(screen.getByText('Test operation 2')).toBeInTheDocument()
    })
  })

  it('should render operation types section', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockOperations
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockOperationTypes
      })

    render(<OperationsPage />)
    
    await waitFor(() => {
      expect(screen.getByText('Operations Without Types (2)')).toBeInTheDocument()
      expect(screen.getByText('Test operation 1')).toBeInTheDocument()
      expect(screen.getByText('Test operation 2')).toBeInTheDocument()
    })
  })

  it('should fetch operations and operation types on component mount', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockOperations
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockOperationTypes
      })

    render(<OperationsPage />)
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/operations/null-types')
      expect(mockFetch).toHaveBeenCalledWith('/api/operation-types')
    })
  })

  it('should handle fetch errors gracefully', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
    
    mockFetch
      .mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ error: 'Internal server error' })
      })
      .mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ error: 'Internal server error' })
      })

    render(<OperationsPage />)
    
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Error fetching operations:', expect.any(Error))
      expect(consoleSpy).toHaveBeenCalledWith('Error fetching operation types:', expect.any(Error))
    })
    
    // Wait for loading state to clear
    await waitFor(() => {
      expect(screen.queryByText('Loading operations...')).not.toBeInTheDocument()
    })
    
    // Component should still render
    expect(screen.getByText('Operations')).toBeInTheDocument()
    
    consoleSpy.mockRestore()
  })

  it('should open assign type dialog when assign button is clicked', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockOperations
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockOperationTypes
      })

    render(<OperationsPage />)
    
    await waitFor(() => {
      expect(screen.getByText('Test operation 1')).toBeInTheDocument()
    })
    
    // Also wait for the loading state to clear
    await waitFor(() => {
      expect(screen.queryByText('Loading operations...')).not.toBeInTheDocument()
    })
    
    const assignButtons = screen.getAllByRole('button', { name: /assign/i })
    fireEvent.click(assignButtons[0])
    
    expect(screen.getByText('Assign Operation Type')).toBeInTheDocument()
    expect(screen.getByText('Select an existing type or create a new one for this operation.')).toBeInTheDocument()
  })







  it('should show loading state while fetching data', async () => {
    mockFetch.mockImplementation(() => new Promise(() => {})) // Never resolves

    render(<OperationsPage />)
    
    expect(screen.getByText('Loading operations...')).toBeInTheDocument()
  })


})
