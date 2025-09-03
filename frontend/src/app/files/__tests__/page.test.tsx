import React from 'react'
import { render, screen, fireEvent, waitFor } from '../../../lib/test-utils'
import FilesPage from '../page'

// Mock fetch globally
const mockFetch = jest.fn()
global.fetch = mockFetch

// Mock File API
const mockFile = new File(['test content'], 'test.pdf', { type: 'application/pdf' })

// Mock FileReader
global.FileReader = jest.fn().mockImplementation(() => ({
  readAsDataURL: jest.fn(),
  onload: null,
  result: 'data:application/pdf;base64,test',
}))

describe('FilesPage Component', () => {
  const mockPDFs = [
    {
      id: 1,
      file_path: '/uploads/test1.pdf',
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
      file_path: '/uploads/test2.pdf',
      client_name: 'Jane Smith',
      account_number: 'MD987654321',
      total_iesiri: 15000.25,
      sold_initial: 8000.00,
      sold_final: 23000.25,
      created_at: '2024-01-16T14:45:00Z',
      operations_count: 30
    }
  ]

  const mockUploadResult = {
    pdf_id: 3,
    operations_stored: 45,
    operations_skipped: 12,
    total_operations_processed: 57,
    deduplication_info: {
      duplicates_found: true,
      duplicate_percentage: 21.1
    },
    pdf_summary: {
      client_name: 'New Client',
      account_number: 'MD111222333',
      sold_initial: 10000.00,
      sold_final: 25000.00
    }
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should render files page header', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFs
      })

      render(<FilesPage />)
      expect(screen.getByText('Files')).toBeInTheDocument()
      expect(screen.getByText('Upload and manage your PDF financial statements.')).toBeInTheDocument()
    })

    it('should render upload section', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFs
      })

      render(<FilesPage />)
      expect(screen.getByText('Upload PDF')).toBeInTheDocument()
      expect(screen.getByText('Upload a PDF financial statement to process and analyze')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument()
    })

    it('should render uploaded files section', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFs
      })

      render(<FilesPage />)
      await waitFor(() => {
        expect(screen.getByText('Uploaded Files (2)')).toBeInTheDocument()
        expect(screen.getByText('Manage your uploaded PDF files and their associated operations')).toBeInTheDocument()
      })
    })

    it('should render upload status section', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFs
      })

      render(<FilesPage />)
      expect(screen.getByText('Upload Status')).toBeInTheDocument()
      expect(screen.getByText('Track your uploaded files and processing status')).toBeInTheDocument()
    })
  })

  describe('File Upload', () => {
    it('should handle file selection', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFs
      })

      render(<FilesPage />)
      
      const fileInput = screen.getByDisplayValue('')
      fireEvent.change(fileInput, { target: { files: [mockFile] } })
      
      expect(screen.getByText('Selected: test.pdf')).toBeInTheDocument()
    })

    it('should enable upload button when file is selected', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFs
      })

      render(<FilesPage />)
      
      const fileInput = screen.getByDisplayValue('')
      const uploadButton = screen.getByRole('button', { name: 'Upload' })
      
      expect(uploadButton).toBeDisabled()
      
      fireEvent.change(fileInput, { target: { files: [mockFile] } })
      
      expect(uploadButton).not.toBeDisabled()
    })

    it('should handle successful file upload', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockUploadResult
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => [
            ...mockPDFs, 
            {
              id: 3,
              file_path: '/uploads/test3.pdf',
              client_name: 'New Client',
              account_number: 'MD111222333',
              total_iesiri: 15000.00,
              sold_initial: 10000.00,
              sold_final: 25000.00,
              created_at: '2024-01-17T12:00:00Z',
              operations_count: 57
            }
          ]
        })

      render(<FilesPage />)
      
      const fileInput = screen.getByDisplayValue('')
      const uploadButton = screen.getByRole('button', { name: 'Upload' })
      
      fireEvent.change(fileInput, { target: { files: [mockFile] } })
      fireEvent.click(uploadButton)
      
      await waitFor(() => {
        expect(screen.getByText('Upload Results')).toBeInTheDocument()
        expect(screen.getByText('45')).toBeInTheDocument() // Operations Stored
        expect(screen.getByText('12')).toBeInTheDocument() // Operations Skipped
        expect(screen.getByText('57')).toBeInTheDocument() // Total Processed
      })
    })

    it('should handle upload failure', async () => {
      const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {})
      
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs
        })
        .mockResolvedValueOnce({
          ok: false,
          json: async () => ({ detail: 'File too large' })
        })

      render(<FilesPage />)
      
      const fileInput = screen.getByDisplayValue('')
      const uploadButton = screen.getByRole('button', { name: 'Upload' })
      
      fireEvent.change(fileInput, { target: { files: [mockFile] } })
      fireEvent.click(uploadButton)
      
      await waitFor(() => {
        expect(alertSpy).toHaveBeenCalledWith('Upload failed: File too large')
      })
      
      alertSpy.mockRestore()
    })

    it('should show uploading state', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs
        })
        .mockImplementation(() => new Promise(() => {})) // Never resolves

      render(<FilesPage />)
      
      const fileInput = screen.getByDisplayValue('')
      const uploadButton = screen.getByRole('button', { name: 'Upload' })
      
      fireEvent.change(fileInput, { target: { files: [mockFile] } })
      fireEvent.click(uploadButton)
      
      expect(screen.getByText('Uploading...')).toBeInTheDocument()
      expect(uploadButton).toBeDisabled()
    })
  })

  describe('Upload Results Display', () => {
    it('should display upload results when available', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockUploadResult
        })

      render(<FilesPage />)
      
      const fileInput = screen.getByDisplayValue('')
      const uploadButton = screen.getByRole('button', { name: 'Upload' })
      
      fireEvent.change(fileInput, { target: { files: [mockFile] } })
      fireEvent.click(uploadButton)
      
      await waitFor(() => {
        expect(screen.getByText('Upload Results')).toBeInTheDocument()
        expect(screen.getByText('Processing results and deduplication information')).toBeInTheDocument()
      })
    })

    it('should display deduplication information', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockUploadResult
        })

      render(<FilesPage />)
      
      const fileInput = screen.getByDisplayValue('')
      const uploadButton = screen.getByRole('button', { name: 'Upload' })
      
      fireEvent.change(fileInput, { target: { files: [mockFile] } })
      fireEvent.click(uploadButton)
      
      await waitFor(() => {
        expect(screen.getByText('Duplicate Detection')).toBeInTheDocument()
        expect(screen.getByText(/Found 12 duplicate operations/)).toBeInTheDocument()
        expect(screen.getByText(/21.1% of total/)).toBeInTheDocument()
      })
    })

    it('should display PDF summary information', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockUploadResult
        })

      render(<FilesPage />)
      
      const fileInput = screen.getByDisplayValue('')
      const uploadButton = screen.getByRole('button', { name: 'Upload' })
      
      fireEvent.change(fileInput, { target: { files: [mockFile] } })
      fireEvent.click(uploadButton)
      
      await waitFor(() => {
        expect(screen.getByText('PDF Summary')).toBeInTheDocument()
        expect(screen.getByText('New Client')).toBeInTheDocument()
        expect(screen.getByText('MD111222333')).toBeInTheDocument()
        expect(screen.getByText('10000.00 LEI')).toBeInTheDocument()
        expect(screen.getByText('25000.00 LEI')).toBeInTheDocument()
      })
    })
  })

  describe('PDF Files Display', () => {
    it('should display uploaded PDFs', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFs
      })

      render(<FilesPage />)
      
      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument()
        expect(screen.getByText('Jane Smith')).toBeInTheDocument()
        expect(screen.getByText('MD123456789')).toBeInTheDocument()
        expect(screen.getByText('MD987654321')).toBeInTheDocument()
      })
    })

    it('should display PDF file information', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFs
      })

      render(<FilesPage />)
      
      await waitFor(() => {
        expect(screen.getByText('25 operations')).toBeInTheDocument()
        expect(screen.getByText('30 operations')).toBeInTheDocument()
        expect(screen.getByText('5000.00 LEI')).toBeInTheDocument()
        expect(screen.getByText('15000.50 LEI')).toBeInTheDocument()
        expect(screen.getByText('test1.pdf')).toBeInTheDocument()
        expect(screen.getByText('test2.pdf')).toBeInTheDocument()
      })
    })

    it('should handle empty PDFs list', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => []
      })

      render(<FilesPage />)
      
      await waitFor(() => {
        expect(screen.getByText('No files uploaded yet.')).toBeInTheDocument()
      })
    })

    it('should handle null values in PDF data', async () => {
      const pdfsWithNulls = [
        {
          id: 3,
          file_path: '/uploads/test3.pdf',
          client_name: null,
          account_number: null,
          total_iesiri: null,
          sold_initial: null,
          sold_final: null,
          created_at: null,
          operations_count: 0
        }
      ]

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => pdfsWithNulls
      })

      render(<FilesPage />)
      
      await waitFor(() => {
        expect(screen.getByText('Unknown Client')).toBeInTheDocument()
        expect(screen.getByText('N/A')).toBeInTheDocument()
        expect(screen.getByText('0 operations')).toBeInTheDocument()
      })
    })
  })

  describe('Delete Operations', () => {
    it('should show delete confirmation dialog', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFs
      })

      render(<FilesPage />)
      
      await waitFor(() => {
        const deleteButtons = screen.getAllByRole('button', { name: /trash/i })
        fireEvent.click(deleteButtons[0])
        
        expect(screen.getByText('Delete this file?')).toBeInTheDocument()
        expect(screen.getByRole('button', { name: 'Yes' })).toBeInTheDocument()
        expect(screen.getByRole('button', { name: 'No' })).toBeInTheDocument()
      })
    })

    it('should handle delete confirmation', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ message: 'PDF deleted successfully' })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs.slice(1) // Remove first PDF
        })

      render(<FilesPage />)
      
      await waitFor(() => {
        const deleteButtons = screen.getAllByRole('button', { name: /trash/i })
        fireEvent.click(deleteButtons[0])
        
        const confirmButton = screen.getByRole('button', { name: 'Yes' })
        fireEvent.click(confirmButton)
      })
      
      await waitFor(() => {
        expect(screen.queryByText('Delete this file?')).not.toBeInTheDocument()
        expect(screen.getByText('Uploaded Files (1)')).toBeInTheDocument()
      })
    })

    it('should handle delete cancellation', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFs
      })

      render(<FilesPage />)
      
      await waitFor(() => {
        const deleteButtons = screen.getAllByRole('button', { name: /trash/i })
        fireEvent.click(deleteButtons[0])
        
        const cancelButton = screen.getByRole('button', { name: 'No' })
        fireEvent.click(cancelButton)
        
        expect(screen.queryByText('Delete this file?')).not.toBeInTheDocument()
      })
    })

    it('should handle delete failure', async () => {
      const alertSpy = jest.spyOn(window, 'alert').mockImplementation(() => {})
      
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs
        })
        .mockResolvedValueOnce({
          ok: false,
          json: async () => ({ detail: 'File not found' })
        })

      render(<FilesPage />)
      
      await waitFor(() => {
        const deleteButtons = screen.getAllByRole('button', { name: /trash/i })
        fireEvent.click(deleteButtons[0])
        
        const confirmButton = screen.getByRole('button', { name: 'Yes' })
        fireEvent.click(confirmButton)
      })
      
      await waitFor(() => {
        expect(alertSpy).toHaveBeenCalledWith('Delete failed: File not found')
      })
      
      alertSpy.mockRestore()
    })

    it('should show deleting state', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs
        })
        .mockImplementation(() => new Promise(() => {})) // Never resolves

      render(<FilesPage />)
      
      await waitFor(() => {
        const deleteButtons = screen.getAllByRole('button', { name: /trash/i })
        fireEvent.click(deleteButtons[0])
        
        const confirmButton = screen.getByRole('button', { name: 'Yes' })
        fireEvent.click(confirmButton)
        
        expect(screen.getByText('Deleting...')).toBeInTheDocument()
      })
    })
  })

  describe('Data Fetching', () => {
    it('should fetch PDFs on component mount', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFs
      })

      render(<FilesPage />)
      
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith('/api/pdfs')
      })
    })

    it('should handle fetch errors gracefully', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
      
      // Mock fetch to simulate a network error
      mockFetch.mockImplementationOnce(() => Promise.reject(new Error('Failed to fetch PDFs')))

      // The component should render without crashing even when fetch fails
      render(<FilesPage />)
      
      // Wait for the error to be logged
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Error fetching PDFs:', expect.any(Error))
      })
      
      // The component should still render the basic structure
      expect(screen.getByText('Files')).toBeInTheDocument()
      
      consoleSpy.mockRestore()
    })
  })

  describe('Navigation Links', () => {
    it('should have link to dashboard', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFs
      })

      render(<FilesPage />)
      
      await waitFor(() => {
        const dashboardLink = screen.getByText('Dashboard')
        expect(dashboardLink).toHaveAttribute('href', '/')
      })
    })
  })

  describe('Responsive Design', () => {
    it('should have proper spacing and padding', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockPDFs
      })

      render(<FilesPage />)
      
      const mainContainer = screen.getByText('Files').closest('.p-8')
      expect(mainContainer).toHaveClass('p-8', 'space-y-6')
    })

    it('should have responsive grid layout for upload results', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockPDFs
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockUploadResult
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => [
            ...mockPDFs, 
            {
              id: 3,
              file_path: '/uploads/test3.pdf',
              client_name: 'New Client',
              account_number: 'MD111222333',
              total_iesiri: 15000.00,
              sold_initial: 10000.00,
              sold_final: 25000.00,
              created_at: '2024-01-17T12:00:00Z',
              operations_count: 57
            }
          ]
        })

      render(<FilesPage />)
      
      // Wait for initial data to load
      await waitFor(() => {
        expect(screen.getByText('John Doe')).toBeInTheDocument()
      })
      
      const fileInput = screen.getByDisplayValue('')
      const uploadButton = screen.getByRole('button', { name: 'Upload' })
      
      fireEvent.change(fileInput, { target: { files: [mockFile] } })
      fireEvent.click(uploadButton)
      
      await waitFor(() => {
        const resultsGrid = screen.getByText('Operations Stored').closest('.grid')
        expect(resultsGrid).toHaveClass('grid-cols-1', 'md:grid-cols-3')
      })
    })
  })
})
