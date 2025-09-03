import React from 'react'
import { render, screen, waitFor } from '../../lib/test-utils'
import Dashboard, { formatCurrency } from '../page'

// Mock fetch globally
const mockFetch = jest.fn()
global.fetch = mockFetch

// Mock Next.js Link component
jest.mock('next/link', () => {
  return function MockLink({ children, href, ...props }: any) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    )
  }
})

describe('Dashboard Component', () => {
  const mockStatistics = {
    total_pdfs: 5,
    total_operations: 150,
    total_iesiri: 50000.75,
    average_amount_per_operation: 333.34
  }

  const mockPDFs = [
    {
      id: 1,
      file_path: '/path/to/file1.pdf',
      client_name: 'John Doe',
      account_number: 'MD123456789',
      total_iesiri: 10000.50,
      sold_initial: 5000.00,
      sold_final: 15000.50,
      created_at: '2024-01-15T10:30:00Z',
      operations_count: 25
    },
    {
      id: 2,
      file_path: '/path/to/file2.pdf',
      client_name: 'Jane Smith',
      account_number: 'MD987654321',
      total_iesiri: 15000.25,
      sold_initial: 8000.00,
      sold_final: 23000.25,
      created_at: '2024-01-16T14:45:00Z',
      operations_count: 30
    }
  ]

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render dashboard header', () => {
      render(<Dashboard />)
      expect(screen.getByText('Dashboard')).toBeInTheDocument()
      expect(screen.getByText('Overview of your financial data and statistics')).toBeInTheDocument()
    })

    it('should render statistics cards when data is loaded', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockStatistics
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs
        })

      render(<Dashboard />)

      await waitFor(() => {
        expect(screen.getByText('Total PDFs')).toBeInTheDocument()
        expect(screen.getByText('Total Operations')).toBeInTheDocument()
        expect(screen.getByText('Total Iesiri')).toBeInTheDocument()
        expect(screen.getByText('Avg per Operation')).toBeInTheDocument()
      })
    })

    it('should render PDFs table when data is loaded', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockStatistics
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs
        })

      render(<Dashboard />)

      await waitFor(() => {
        expect(screen.getByText('Processed PDFs')).toBeInTheDocument()
        expect(screen.getByText('List of all processed financial statements')).toBeInTheDocument()
      })
    })
  })

  describe('Statistics Display', () => {
    it('should display correct statistics values', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockStatistics
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs
        })

      render(<Dashboard />)

      await waitFor(() => {
        expect(screen.getByText('5')).toBeInTheDocument() // Total PDFs
        expect(screen.getByText('150')).toBeInTheDocument() // Total Operations
        expect(screen.getByText('MDL\u00A050,000.75')).toBeInTheDocument() // Total Iesiri
        expect(screen.getByText('MDL\u00A0333.34')).toBeInTheDocument() // Avg per Operation
      })
    })

    it('should display currency formatting correctly', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockStatistics
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs
        })

      render(<Dashboard />)

      await waitFor(() => {
        // Check that currency values are properly formatted
        expect(screen.getByText('MDL\u00A050,000.75')).toBeInTheDocument()
        expect(screen.getByText('MDL\u00A0333.34')).toBeInTheDocument()
      })
    })
  })

  describe('PDFs Table', () => {
    it('should display all PDF data in table', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockStatistics
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs
        })

      render(<Dashboard />)

      await waitFor(() => {
        // Check table headers
        expect(screen.getByText('ID')).toBeInTheDocument()
        expect(screen.getByText('Client')).toBeInTheDocument()
        expect(screen.getByText('Account')).toBeInTheDocument()
        expect(screen.getByText('Operations')).toBeInTheDocument()
        expect(screen.getByText('Total Iesiri')).toBeInTheDocument()
        expect(screen.getByText('Initial Balance')).toBeInTheDocument()
        expect(screen.getByText('Final Balance')).toBeInTheDocument()
        expect(screen.getByText('File')).toBeInTheDocument()
      })

      // Wait for table data to be rendered
      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument()
        expect(screen.getByText('MD123456789')).toBeInTheDocument()
        expect(screen.getByText('25')).toBeInTheDocument()
        expect(screen.getByText('MDL\u00A010,000.50')).toBeInTheDocument()
        expect(screen.getByText('MDL\u00A05,000.00')).toBeInTheDocument()
        expect(screen.getByText('MDL\u00A015,000.50')).toBeInTheDocument()
      })
    })

    it('should display operations count as badge', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockStatistics
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs
        })

      render(<Dashboard />)

      await waitFor(() => {
        const operationsBadge = screen.getByText('25')
        expect(operationsBadge).toHaveClass('inline-flex', 'items-center', 'px-2', 'py-1', 'rounded-full', 'text-xs', 'font-medium', 'bg-blue-100', 'text-blue-800')
      })
    })

    it('should display view details links for each PDF', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockStatistics
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs
        })

      render(<Dashboard />)

      await waitFor(() => {
        const viewDetailsLinks = screen.getAllByText('View Details')
        expect(viewDetailsLinks).toHaveLength(2)
        
        // Check that links have correct hrefs
        expect(viewDetailsLinks[0]).toHaveAttribute('href', '/pdf/1')
        expect(viewDetailsLinks[1]).toHaveAttribute('href', '/pdf/2')
      })
    })

    it('should handle null values in PDF data', async () => {
      const pdfsWithNulls = [
        {
          id: 3,
          file_path: '/path/to/file3.pdf',
          client_name: null,
          account_number: null,
          total_iesiri: null,
          sold_initial: null,
          sold_final: null,
          created_at: null,
          operations_count: 0
        }
      ]

      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockStatistics
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => pdfsWithNulls
        })

      render(<Dashboard />)

      await waitFor(() => {
        expect(screen.getByText('N/A')).toBeInTheDocument()
        expect(screen.getByText('0')).toBeInTheDocument()
      })
    })
  })

  describe('Data Fetching', () => {
    it('should fetch statistics and PDFs on component mount', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockStatistics
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs
        })

      render(<Dashboard />)

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledTimes(2)
        expect(mockFetch).toHaveBeenNthCalledWith(1, '/api/statistics')
        expect(mockFetch).toHaveBeenNthCalledWith(2, '/api/pdfs')
      })
    })

    it('should handle fetch errors gracefully', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
      
      mockFetch
        .mockRejectedValueOnce(new Error('Failed to fetch statistics'))
        .mockRejectedValueOnce(new Error('Failed to fetch PDFs'))

      render(<Dashboard />)

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Error fetching statistics:', expect.any(Error))
        expect(consoleSpy).toHaveBeenCalledWith('Error fetching PDFs:', expect.any(Error))
      })

      consoleSpy.mockRestore()
    })

    it('should handle empty data arrays', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ ...mockStatistics, total_pdfs: 0, total_operations: 0 })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => []
        })

      render(<Dashboard />)

      await waitFor(() => {
        expect(screen.getByText('0')).toBeInTheDocument() // Total PDFs
        expect(screen.getByText('0')).toBeInTheDocument() // Total Operations
      })

      // Table should still be rendered but empty
      expect(screen.getByText('Processed PDFs')).toBeInTheDocument()
    })
  })

  describe('Currency Formatting', () => {
    it('should format positive amounts correctly', () => {
      expect(formatCurrency(1234.56)).toBe('MDL\u00A01,234.56')
      expect(formatCurrency(1000000)).toBe('MDL\u00A01,000,000.00')
    })

    it('should handle null amounts', () => {
      expect(formatCurrency(null)).toBe('N/A')
    })

    it('should handle zero amounts', () => {
      expect(formatCurrency(0)).toBe('MDL\u00A00.00')
    })

    it('should handle decimal amounts', () => {
      expect(formatCurrency(0.99)).toBe('MDL\u00A00.99')
      expect(formatCurrency(123.456)).toBe('MDL\u00A0123.46') // Rounds to 2 decimal places
    })
  })

  describe('Loading States', () => {
    it('should not display statistics cards before data loads', () => {
      mockFetch.mockImplementation(() => new Promise(() => {})) // Never resolves

      render(<Dashboard />)

      expect(screen.queryByText('Total PDFs')).not.toBeInTheDocument()
      expect(screen.queryByText('Total Operations')).not.toBeInTheDocument()
    })

    it('should display PDFs table structure even before data loads', () => {
      mockFetch.mockImplementation(() => new Promise(() => {})) // Never resolves

      render(<Dashboard />)

      // The table structure is always rendered, just without data
      expect(screen.getByText('Processed PDFs')).toBeInTheDocument()
    })
  })

  describe('Responsive Design', () => {
    it('should have responsive grid layout for statistics cards', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockStatistics
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs
        })

      render(<Dashboard />)

      await waitFor(() => {
        const statsGrid = screen.getByText('Total PDFs').closest('.grid')
        expect(statsGrid).toHaveClass('grid-cols-1', 'md:grid-cols-2', 'lg:grid-cols-4')
      })
    })

    it('should have proper spacing and padding', () => {
      render(<Dashboard />)
      
      const mainContainer = screen.getByText('Dashboard').closest('.p-8')
      expect(mainContainer).toHaveClass('p-8', 'space-y-6')
    })
  })
})
