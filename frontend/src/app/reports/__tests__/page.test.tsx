import React from 'react'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import ReportsPage from '../page'

// Mock recharts components
jest.mock('recharts', () => ({
  PieChart: ({ children }: { children: React.ReactNode }) => <div data-testid="pie-chart">{children}</div>,
  Pie: ({ children, onClick }: { children: React.ReactNode; onClick: (data: any) => void }) => (
    <div data-testid="pie" onClick={() => onClick({ name: 'Test Category' })}>
      {children}
    </div>
  ),
  Cell: ({ children }: { children: React.ReactNode }) => <div data-testid="cell">{children}</div>,
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div data-testid="responsive-container">{children}</div>,
  Tooltip: ({ children }: { children: React.ReactNode }) => <div data-testid="tooltip">{children}</div>,
  Legend: ({ children }: { children: React.ReactNode }) => <div data-testid="legend">{children}</div>
}))

// Mock date-fns
jest.mock('date-fns', () => ({
  format: jest.fn((date, format) => '15.01.2024'),
  parseISO: jest.fn((date) => new Date(date))
}))

// Mock the fetch API
const mockFetch = jest.fn()
global.fetch = mockFetch

const mockAvailableMonths = [
  { year: 2024, month: 1, label: '2024-01' },
  { year: 2024, month: 2, label: '2024-02' }
]

const mockMonthlyReport = {
  year: 2024,
  month: 1,
  total_amount: 15000.50,
  total_operations: 25,
  type_groups: [
    {
      type_id: 1,
      type_name: 'Groceries',
      total_amount: 8000.25,
      operation_count: 12,
      operations: []
    },
    {
      type_id: 2,
      type_name: 'Transport',
      total_amount: 3000.00,
      operation_count: 8,
      operations: []
    },
    {
      type_id: null,
      type_name: 'Uncategorized',
      total_amount: 4000.25,
      operation_count: 5,
      operations: []
    }
  ],
  pie_chart_data: [
    { name: 'Groceries', value: 8000.25, color: '#3B82F6' },
    { name: 'Transport', value: 3000.00, color: '#10B981' },
    { name: 'Uncategorized', value: 4000.25, color: '#F59E0B' }
  ],
  summary: {
    average_amount_per_operation: 600.02,
    most_expensive_type: 'Groceries',
    most_expensive_amount: 8000.25
  }
}

describe('ReportsPage Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should render the page header correctly', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAvailableMonths
    })

    render(<ReportsPage />)

    await waitFor(() => {
      expect(screen.getByText('Financial Reports')).toBeInTheDocument()
    })
  })

  it('should fetch available months on component mount', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockAvailableMonths
    })

    render(<ReportsPage />)

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/reports/available-months')
    })
  })

  it('should display monthly report statistics', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAvailableMonths
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockMonthlyReport
      })

    render(<ReportsPage />)

    await waitFor(() => {
      expect(screen.getByText('Total Amount')).toBeInTheDocument()
      expect(screen.getByText('Total Operations')).toBeInTheDocument()
    })

    await waitFor(() => {
      expect(screen.getByText('MDL 15,000.50')).toBeInTheDocument()
      expect(screen.getByText('25')).toBeInTheDocument()
    })
  })

  it('should display pie chart section', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAvailableMonths
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockMonthlyReport
      })

    render(<ReportsPage />)

    await waitFor(() => {
      expect(screen.getByText('Spending Distribution')).toBeInTheDocument()
      expect(screen.getByTestId('pie-chart')).toBeInTheDocument()
    })
  })

  it('should handle fetch errors gracefully', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))

    render(<ReportsPage />)

    await waitFor(() => {
      expect(screen.getByText('Financial Reports')).toBeInTheDocument()
    })
  })

  it('should display all summary statistics correctly', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAvailableMonths
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockMonthlyReport
      })

    render(<ReportsPage />)

    // Wait for the data to be fetched and rendered
    await waitFor(() => {
      expect(screen.getByText('Total Amount')).toBeInTheDocument()
      expect(screen.getByText('Total Operations')).toBeInTheDocument()
    })

    // Wait for the actual values to be displayed
    await waitFor(() => {
      expect(screen.getByText('MDL 15,000.50')).toBeInTheDocument()
      expect(screen.getByText('25')).toBeInTheDocument()
      expect(screen.getByText('MDL 600.02')).toBeInTheDocument()
      // Use getAllByText since there are multiple "Groceries" elements
      expect(screen.getAllByText('Groceries')).toHaveLength(2)
      expect(screen.getByText('MDL 8,000.25')).toBeInTheDocument()
    })
  })

  it('should handle month selection change', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAvailableMonths
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockMonthlyReport
      })

    render(<ReportsPage />)

    // Wait for the month to be selected and displayed
    await waitFor(() => {
      expect(screen.getByText('2024-01')).toBeInTheDocument()
    })

    // Month selection should trigger report fetch
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/reports/monthly/2024/1')
    })
  })

  it('should display pie chart when data is available', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAvailableMonths
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockMonthlyReport
      })

    render(<ReportsPage />)

    await waitFor(() => {
      expect(screen.getByTestId('pie-chart')).toBeInTheDocument()
      expect(screen.getByTestId('pie')).toBeInTheDocument()
    })
  })

  it('should handle no data available state', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAvailableMonths
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => null
      })

    render(<ReportsPage />)

    await waitFor(() => {
      expect(screen.getByText('No Data Available')).toBeInTheDocument()
      expect(screen.getByText('No financial data found for the selected month.')).toBeInTheDocument()
    })
  })

  it('should handle empty pie chart data', async () => {
    const emptyReport = {
      ...mockMonthlyReport,
      pie_chart_data: []
    }

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAvailableMonths
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => emptyReport
      })

    render(<ReportsPage />)

    await waitFor(() => {
      expect(screen.getByText('No data available for this month.')).toBeInTheDocument()
    })
  })

  it('should handle fetch errors for monthly report', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAvailableMonths
      })
      .mockRejectedValueOnce(new Error('Failed to fetch report'))

    render(<ReportsPage />)

    await waitFor(() => {
      expect(screen.getByText('Financial Reports')).toBeInTheDocument()
    })
  })

  it('should handle month selection with no available months', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => []
    })

    render(<ReportsPage />)

    await waitFor(() => {
      expect(screen.getByText('Financial Reports')).toBeInTheDocument()
    })

    // Should not crash when no months are available
    expect(screen.getByText('Select month')).toBeInTheDocument()
  })

  it('should handle non-ok response for available months', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500
    })

    render(<ReportsPage />)

    await waitFor(() => {
      expect(screen.getByText('Financial Reports')).toBeInTheDocument()
    })
  })

  it('should handle non-ok response for monthly report', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockAvailableMonths
      })
      .mockResolvedValueOnce({
        ok: false,
        status: 500
      })

    render(<ReportsPage />)

    await waitFor(() => {
      expect(screen.getByText('Financial Reports')).toBeInTheDocument()
    })
  })
})
