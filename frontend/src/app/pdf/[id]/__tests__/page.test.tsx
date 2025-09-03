import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import PDFDetailsPage from '../page'

// Mock next/link
jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  )
})

// Mock the fetch API
const mockFetch = jest.fn()
global.fetch = mockFetch

const mockPDFDetails = {
  pdf: {
    id: 1,
    file_path: '/uploads/test.pdf',
    client_name: 'John Doe',
    account_number: 'MD123456789',
    total_iesiri: 10000.50,
    sold_initial: 5000.00,
    sold_final: 15000.50,
    created_at: '2024-01-15T10:30:00Z'
  },
  operations: [
    {
      id: 1,
      pdf_id: 1,
      transaction_date: '2024-01-15T09:00:00Z',
      processed_date: '2024-01-15T09:05:00Z',
      description: 'ATM Withdrawal',
      amount_lei: -500.00
    },
    {
      id: 2,
      pdf_id: 1,
      transaction_date: '2024-01-15T10:00:00Z',
      processed_date: '2024-01-15T10:05:00Z',
      description: 'Salary Deposit',
      amount_lei: 2500.00
    }
  ]
}

describe('PDFDetailsPage Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render the page header correctly', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFDetails
      })

      render(<PDFDetailsPage params={{ id: '1' }} />)

      await waitFor(() => {
        expect(screen.getByText('PDF Details')).toBeInTheDocument()
        expect(screen.getByText('Financial statement analysis')).toBeInTheDocument()
      })
    })

    it('should render back to dashboard button', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFDetails
      })

      render(<PDFDetailsPage params={{ id: '1' }} />)

      await waitFor(() => {
        const backButton = screen.getByRole('link', { name: /back to dashboard/i })
        expect(backButton).toBeInTheDocument()
        expect(backButton).toHaveAttribute('href', '/')
      })
    })
  })

  describe('Data Display', () => {
    it('should display PDF summary information correctly', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFDetails
      })

      render(<PDFDetailsPage params={{ id: '1' }} />)

      await waitFor(() => {
        // Client information
        expect(screen.getByText('John Doe')).toBeInTheDocument()
        expect(screen.getByText('MD123456789')).toBeInTheDocument()
        
        // Total Iesiri
        expect(screen.getByText('MDL 10,000.50')).toBeInTheDocument()
        
        // Balance Range
        expect(screen.getByText('Initial: MDL 5,000.00')).toBeInTheDocument()
        expect(screen.getByText('Final: MDL 15,000.50')).toBeInTheDocument()
      })
    })

    it('should display operations table correctly', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFDetails
      })

      render(<PDFDetailsPage params={{ id: '1' }} />)

      await waitFor(() => {
        expect(screen.getByText('Operations (2)')).toBeInTheDocument()
        expect(screen.getByText('Detailed list of all financial operations')).toBeInTheDocument()
        
        // Table headers
        expect(screen.getByText('Date')).toBeInTheDocument()
        expect(screen.getByText('Processed')).toBeInTheDocument()
        expect(screen.getByText('Description')).toBeInTheDocument()
        expect(screen.getByText('Amount')).toBeInTheDocument()
        
        // Operation data
        expect(screen.getByText('ATM Withdrawal')).toBeInTheDocument()
        expect(screen.getByText('Salary Deposit')).toBeInTheDocument()
        expect(screen.getByText('-MDL 500.00')).toBeInTheDocument()
        expect(screen.getByText('MDL 2,500.00')).toBeInTheDocument()
      })
    })
  })

  describe('Loading States', () => {
    it('should show loading state initially', () => {
      mockFetch.mockImplementation(() => new Promise(() => {})) // Never resolves

      render(<PDFDetailsPage params={{ id: '1' }} />)

      expect(screen.getByText('Loading...')).toBeInTheDocument()
    })
  })

  describe('Error Handling', () => {
    it('should show error state when PDF is not found', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404
      })

      render(<PDFDetailsPage params={{ id: '999' }} />)

      await waitFor(() => {
        expect(screen.getByText('PDF not found')).toBeInTheDocument()
      })
    })

    it('should handle fetch errors gracefully', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      render(<PDFDetailsPage params={{ id: '1' }} />)

      await waitFor(() => {
        expect(screen.getByText('PDF not found')).toBeInTheDocument()
      })
    })
  })

  describe('Data Fetching', () => {
    it('should fetch PDF details on component mount', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFDetails
      })

      render(<PDFDetailsPage params={{ id: '1' }} />)

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/pdfs/1')
      })
    })

    it('should refetch when params.id changes', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFDetails
      })

      const { rerender } = render(<PDFDetailsPage params={{ id: '1' }} />)

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/pdfs/1')
      })

      // Change the ID
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ...mockPDFDetails, pdf: { ...mockPDFDetails.pdf, id: 2 } })
      })

      rerender(<PDFDetailsPage params={{ id: '2' }} />)

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/pdfs/2')
      })
    })
  })

  describe('Formatting Functions', () => {
    it('should format currency correctly', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFDetails
      })

      render(<PDFDetailsPage params={{ id: '1' }} />)

      await waitFor(() => {
        expect(screen.getByText(/MDL 10,000\.50/)).toBeInTheDocument()
        expect(screen.getByText(/MDL 5,000\.00/)).toBeInTheDocument()
        expect(screen.getByText(/MDL 15,000\.50/)).toBeInTheDocument()
      })
    })

    it('should format dates correctly', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFDetails
      })

      render(<PDFDetailsPage params={{ id: '1' }} />)

      await waitFor(() => {
        // The dates should be formatted according to locale
        expect(screen.getAllByText(/1\/15\/2024/)).toHaveLength(4) // 2 operations × 2 dates each
      })
    })

    it('should handle null values gracefully', async () => {
      const mockDataWithNulls = {
        pdf: {
          id: 1,
          file_path: '/uploads/test.pdf',
          client_name: null,
          account_number: null,
          total_iesiri: null,
          sold_initial: null,
          sold_final: null,
          created_at: null
        },
        operations: [
          {
            id: 1,
            pdf_id: 1,
            transaction_date: null,
            processed_date: null,
            description: null,
            amount_lei: null
          }
        ]
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockDataWithNulls
      })

      render(<PDFDetailsPage params={{ id: '1' }} />)

      await waitFor(() => {
        expect(screen.getAllByText('N/A')).toHaveLength(6) // Multiple N/A values for null fields
        expect(screen.getByText('No account number')).toBeInTheDocument()
      })
    })
  })
})
