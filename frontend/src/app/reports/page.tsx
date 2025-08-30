'use client'

import { useState, useEffect } from 'react'
import { FileText, Calendar, PieChart, BarChart3, Eye, ChevronRight } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { PieChart as RechartsPieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { format, parseISO } from 'date-fns'

interface AvailableMonth {
  year: number
  month: number
  label: string
}

interface PieChartData {
  name: string
  value: number
  color: string
  type_id?: number | null
}

interface Operation {
  id: number
  transaction_date: string
  processed_date: string
  description: string
  amount_lei: number
}

interface TypeGroup {
  type_id: number | null
  type_name: string
  total_amount: number
  operation_count: number
  operations: Operation[]
}

interface MonthlyReport {
  year: number
  month: number
  total_amount: number
  total_operations: number
  type_groups: TypeGroup[]
  pie_chart_data: PieChartData[]
  summary: {
    average_amount_per_operation: number
    most_expensive_type: string | null
    most_expensive_amount: number
  }
}

interface TypeOperations {
  type: {
    id: number
    name: string
    description: string | null
  }
  year: number
  month: number
  operations: Operation[]
  pagination: {
    limit: number
    offset: number
    total: number
    has_more: boolean
  }
}

export default function ReportsPage() {
  const [availableMonths, setAvailableMonths] = useState<AvailableMonth[]>([])
  const [selectedMonth, setSelectedMonth] = useState<string>('')
  const [reportData, setReportData] = useState<MonthlyReport | null>(null)
  const [loading, setLoading] = useState(false)
  const [selectedTypeGroup, setSelectedTypeGroup] = useState<TypeGroup | null>(null)
  const [typeOperations, setTypeOperations] = useState<TypeOperations | null>(null)
  const [showAllOperations, setShowAllOperations] = useState(false)
  const [selectedPieSlice, setSelectedPieSlice] = useState<string | null>(null)

  // Fetch available months on component mount
  useEffect(() => {
    fetchAvailableMonths()
  }, [])

  // Fetch report data when month changes
  useEffect(() => {
    if (selectedMonth) {
      fetchMonthlyReport()
      // Reset pie slice selection when month changes
      setSelectedPieSlice(null)
      setSelectedTypeGroup(null)
      setTypeOperations(null)
      setShowAllOperations(false)
    }
  }, [selectedMonth])

  const fetchAvailableMonths = async () => {
    try {
      const response = await fetch('http://localhost:8000/reports/available-months')
      if (response.ok) {
        const months = await response.json()
        setAvailableMonths(months)
        if (months.length > 0) {
          setSelectedMonth(months[0].label)
        }
      }
    } catch (error) {
      console.error('Error fetching available months:', error)
    }
  }

  const fetchMonthlyReport = async () => {
    if (!selectedMonth) return
    
    setLoading(true)
    try {
      const [year, month] = selectedMonth.split('-').map(Number)
      const response = await fetch(`http://localhost:8000/reports/monthly/${year}/${month}`)
      if (response.ok) {
        const data = await response.json()
        setReportData(data)
      }
    } catch (error) {
      console.error('Error fetching monthly report:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchTypeOperations = async (typeId: number, limit: number = 10, offset: number = 0) => {
    if (!selectedMonth || !typeId) return
    
    try {
      const [year, month] = selectedMonth.split('-').map(Number)
      const response = await fetch(
        `http://localhost:8000/reports/monthly/${year}/${month}/type/${typeId}?limit=${limit}&offset=${offset}`
      )
      if (response.ok) {
        const data = await response.json()
        setTypeOperations(data)
      }
    } catch (error) {
      console.error('Error fetching type operations:', error)
    }
  }

  const handlePieSliceClick = (data: any) => {
    if (data && data.name) {
      setSelectedPieSlice(data.name)
      
      // Find the corresponding type group
      const typeGroup = reportData?.type_groups.find(group => group.type_name === data.name)
      if (typeGroup) {
        setSelectedTypeGroup(typeGroup)
        if (typeGroup.type_id) {
          fetchTypeOperations(typeGroup.type_id)
        }
      }
    }
  }

  const handleTypeGroupClick = (group: TypeGroup) => {
    setSelectedTypeGroup(group)
    setSelectedPieSlice(group.type_name)
    if (group.type_id) {
      fetchTypeOperations(group.type_id)
    }
  }

  const handleShowAllOperations = (group: TypeGroup) => {
    setSelectedTypeGroup(group)
    setSelectedPieSlice(group.type_name)
    setShowAllOperations(true)
    if (group.type_id) {
      fetchTypeOperations(group.type_id, 1000, 0) // Get all operations
    }
  }

  const clearSelection = () => {
    setSelectedPieSlice(null)
    setSelectedTypeGroup(null)
    setTypeOperations(null)
    setShowAllOperations(false)
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('md-MD', {
      style: 'currency',
      currency: 'MDL'
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    try {
      return format(parseISO(dateString), 'dd.MM.yyyy')
    } catch {
      return dateString
    }
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border rounded-lg shadow-lg">
          <p className="font-medium">{payload[0].name}</p>
          <p className="text-sm text-gray-600">
            {formatCurrency(payload[0].value)}
          </p>
          <p className="text-xs text-gray-500">
            {((payload[0].value / reportData!.total_amount) * 100).toFixed(1)}%
          </p>
        </div>
      )
    }
    return null
  }

  // Filter type groups based on selected pie slice
  const filteredTypeGroups = selectedPieSlice 
    ? reportData?.type_groups.filter(group => group.type_name === selectedPieSlice) || []
    : reportData?.type_groups || []

  return (
    <div className="p-8 space-y-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Reports</h1>
        <p className="text-muted-foreground">
          Generate and view financial reports and analytics by month.
        </p>
      </div>

      {/* Month Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Select Month
          </CardTitle>
          <CardDescription>
            Choose a month to view detailed financial reports and analytics.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <Select value={selectedMonth} onValueChange={setSelectedMonth}>
              <SelectTrigger className="w-64">
                <SelectValue placeholder="Select a month" />
              </SelectTrigger>
              <SelectContent>
                {availableMonths.map((month) => (
                  <SelectItem key={month.label} value={month.label}>
                    {month.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {loading && <div className="text-sm text-muted-foreground">Loading...</div>}
          </div>
        </CardContent>
      </Card>

      {/* Monthly Report */}
      {reportData && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Total Amount</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(reportData.total_amount)}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Total Operations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{reportData.total_operations}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Average per Operation</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(reportData.summary.average_amount_per_operation)}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Largest Category</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-lg font-bold">
                  {reportData.summary.most_expensive_type || 'N/A'}
                </div>
                <div className="text-sm text-muted-foreground">
                  {formatCurrency(reportData.summary.most_expensive_amount)}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Pie Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChart className="h-5 w-5" />
                Spending Distribution
              </CardTitle>
              <CardDescription>
                Click on any slice to filter operations below by that category.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {reportData.pie_chart_data.length > 0 ? (
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsPieChart>
                      <Pie
                        data={reportData.pie_chart_data}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={120}
                        fill="#8884d8"
                        dataKey="value"
                        onClick={handlePieSliceClick}
                        style={{ cursor: 'pointer' }}
                      >
                        {reportData.pie_chart_data.map((entry, index) => (
                          <Cell 
                            key={`cell-${index}`} 
                            fill={entry.color}
                            style={{ 
                              cursor: 'pointer',
                              opacity: selectedPieSlice && selectedPieSlice !== entry.name ? 0.5 : 1
                            }}
                          />
                        ))}
                      </Pie>
                      <Tooltip content={<CustomTooltip />} />
                      <Legend />
                    </RechartsPieChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  No data available for this month.
                </div>
              )}
            </CardContent>
          </Card>

          {/* Type Groups */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    {selectedPieSlice ? `${selectedPieSlice} Operations` : 'Operation Types Breakdown'}
                  </CardTitle>
                  <CardDescription>
                    {selectedPieSlice 
                      ? `Showing operations for ${selectedPieSlice} category.`
                      : 'Click on any category to view top 10 operations, or click "Details" to see all operations.'
                    }
                  </CardDescription>
                </div>
                {selectedPieSlice && (
                  <Button variant="outline" size="sm" onClick={clearSelection}>
                    Show All Categories
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredTypeGroups.map((group) => (
                  <div key={group.type_name} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h3 className="font-semibold text-lg">{group.type_name}</h3>
                        <p className="text-sm text-muted-foreground">
                          {group.operation_count} operations
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-xl font-bold">{formatCurrency(group.total_amount)}</div>
                        <div className="text-sm text-muted-foreground">
                          {((group.total_amount / reportData.total_amount) * 100).toFixed(1)}%
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleTypeGroupClick(group)}
                        className="flex items-center gap-2"
                      >
                        <Eye className="h-4 w-4" />
                        Top 10
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleShowAllOperations(group)}
                        className="flex items-center gap-2"
                      >
                        <ChevronRight className="h-4 w-4" />
                        All Details
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Type Operations Modal/Dialog */}
          {selectedTypeGroup && typeOperations && (
            <Card>
              <CardHeader>
                <CardTitle>
                  {typeOperations.type.name} - {selectedMonth}
                </CardTitle>
                <CardDescription>
                  {showAllOperations ? 'All operations' : 'Top 10 operations by amount'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead className="text-right">Amount</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {typeOperations.operations.map((operation) => (
                      <TableRow key={operation.id}>
                        <TableCell>{formatDate(operation.transaction_date)}</TableCell>
                        <TableCell className="max-w-md truncate">
                          {operation.description}
                        </TableCell>
                        <TableCell className="text-right font-medium">
                          {formatCurrency(operation.amount_lei)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                
                {typeOperations.pagination.has_more && !showAllOperations && (
                  <div className="mt-4 flex justify-center">
                    <Button
                      variant="outline"
                      onClick={() => fetchTypeOperations(
                        typeOperations.type.id,
                        typeOperations.pagination.limit,
                        typeOperations.pagination.offset + typeOperations.pagination.limit
                      )}
                    >
                      Load More
                    </Button>
                  </div>
                )}
                
                <div className="mt-4 flex justify-end">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setSelectedTypeGroup(null)
                      setTypeOperations(null)
                      setShowAllOperations(false)
                    }}
                  >
                    Close
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}

      {!reportData && !loading && selectedMonth && (
        <Card>
          <CardContent className="text-center py-12">
            <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No Data Available</h3>
            <p className="text-muted-foreground">
              No financial data found for the selected month.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
