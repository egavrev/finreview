'use client'

import { useState, useEffect } from 'react'
import { FileText, Calendar, PieChart, BarChart3, Eye, ChevronRight, Clock, TrendingUp } from 'lucide-react'
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
      const data = payload[0]
      const percentage = ((data.value / reportData!.total_amount) * 100).toFixed(1)
      return (
        <div className="bg-white p-4 border rounded-lg shadow-xl border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: data.color }}
            />
            <p className="font-semibold text-gray-900">{data.name}</p>
          </div>
          <div className="space-y-1">
            <p className="text-lg font-bold text-gray-900">
              {formatCurrency(data.value)}
            </p>
            <p className="text-sm text-gray-600">
              {percentage}% of total
            </p>
          </div>
        </div>
      )
    }
    return null
  }

  const CustomLegend = ({ payload }: any) => {
    if (!payload || !reportData) return null

    return (
      <div className="mt-6">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {payload.map((entry: any, index: number) => {
            const percentage = ((entry.value / reportData.total_amount) * 100).toFixed(1)
            const isSelected = selectedPieSlice === entry.value
            return (
              <div
                key={index}
                className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-all duration-200 ${
                  isSelected 
                    ? 'bg-blue-50 border border-blue-200' 
                    : 'hover:bg-gray-50'
                }`}
                onClick={() => handlePieSliceClick({ name: entry.value })}
              >
                <div 
                  className="w-3 h-3 rounded-full flex-shrink-0" 
                  style={{ backgroundColor: entry.color }}
                />
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {entry.value}
                  </p>
                  <p className="text-xs text-gray-500">
                    {percentage}% • {formatCurrency(entry.payload.value)}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    )
  }

  // Custom label renderer for pie chart
  const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, name }: any) => {
    const RADIAN = Math.PI / 180
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5
    const x = cx + radius * Math.cos(-midAngle * RADIAN)
    const y = cy + radius * Math.sin(-midAngle * RADIAN)

    // Only show labels for slices with more than 5% or if it's the selected slice
    const shouldShowLabel = (percent || 0) > 0.05 || selectedPieSlice === name

    if (!shouldShowLabel) return null

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        className="text-xs font-medium drop-shadow-sm"
      >
        {(percent || 0) > 0.05 ? `${((percent || 0) * 100).toFixed(0)}%` : ''}
      </text>
    )
  }

  // Filter type groups based on selected pie slice
  const filteredTypeGroups = selectedPieSlice 
    ? reportData?.type_groups.filter(group => group.type_name === selectedPieSlice) || []
    : reportData?.type_groups || []

  return (
    <div className="p-6 lg:p-8 space-y-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
          Financial Reports
        </h1>
        <p className="text-muted-foreground text-lg">
          Generate and view comprehensive financial reports and analytics by month.
        </p>
      </div>

      {/* Month Selection */}
      <Card className="border-0 shadow-lg bg-gradient-to-r from-white to-gray-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-gray-800">
            <Calendar className="h-5 w-5 text-blue-600" />
            Select Month
          </CardTitle>
          <CardDescription className="text-gray-600">
            Choose a month to view detailed financial reports and analytics.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <Select value={selectedMonth} onValueChange={setSelectedMonth}>
              <SelectTrigger className="w-64 border-gray-300 focus:border-blue-500 focus:ring-blue-500">
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
            {loading && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                Loading...
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Monthly Report */}
      {reportData && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-50 to-blue-100">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-blue-800 flex items-center gap-2">
                  <TrendingUp className="h-4 w-4" />
                  Total Amount
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-900">{formatCurrency(reportData.total_amount)}</div>
              </CardContent>
            </Card>
            <Card className="border-0 shadow-lg bg-gradient-to-br from-green-50 to-green-100">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-green-800 flex items-center gap-2">
                  <BarChart3 className="h-4 w-4" />
                  Total Operations
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-900">{reportData.total_operations}</div>
              </CardContent>
            </Card>
            <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-50 to-purple-100">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-purple-800 flex items-center gap-2">
                  <PieChart className="h-4 w-4" />
                  Average per Operation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-purple-900">
                  {formatCurrency(reportData.summary.average_amount_per_operation)}
                </div>
              </CardContent>
            </Card>
            <Card className="border-0 shadow-lg bg-gradient-to-br from-orange-50 to-orange-100">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-orange-800 flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  Largest Category
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-lg font-bold text-orange-900">
                  {reportData.summary.most_expensive_type || 'N/A'}
                </div>
                <div className="text-sm text-orange-700">
                  {formatCurrency(reportData.summary.most_expensive_amount)}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Pie Chart */}
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-gray-800">
                <Clock className="h-5 w-5 text-blue-600" />
                Spending Distribution
              </CardTitle>
              <CardDescription className="text-gray-600">
                Click on any slice or legend item to filter operations below by that category.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {reportData.pie_chart_data.length > 0 ? (
                <div className="space-y-6">
                  <div className="h-96">
                    <ResponsiveContainer width="100%" height="100%">
                      <RechartsPieChart>
                        <Pie
                          data={reportData.pie_chart_data}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={renderCustomLabel}
                          outerRadius={140}
                          innerRadius={60}
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
                                opacity: selectedPieSlice && selectedPieSlice !== entry.name ? 0.4 : 1,
                                transition: 'opacity 0.2s ease-in-out'
                              }}
                            />
                          ))}
                        </Pie>
                        <Tooltip content={<CustomTooltip />} />
                      </RechartsPieChart>
                    </ResponsiveContainer>
                  </div>
                  <CustomLegend payload={reportData.pie_chart_data.map((entry, index) => ({
                    value: entry.name,
                    color: entry.color,
                    payload: entry
                  }))} />
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <PieChart className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p className="text-lg font-medium">No data available for this month.</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Type Groups */}
          <Card className="border-0 shadow-lg">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2 text-gray-800">
                    <BarChart3 className="h-5 w-5 text-blue-600" />
                    {selectedPieSlice ? `${selectedPieSlice} Operations` : 'Operation Types Breakdown'}
                  </CardTitle>
                  <CardDescription className="text-gray-600">
                    {selectedPieSlice 
                      ? `Showing operations for ${selectedPieSlice} category.`
                      : 'Click on any category to view top 10 operations, or click "Details" to see all operations.'
                    }
                  </CardDescription>
                </div>
                {selectedPieSlice && (
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={clearSelection}
                    className="border-gray-300 hover:bg-gray-50"
                  >
                    Show All Categories
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {filteredTypeGroups.map((group) => (
                  <div key={group.type_name} className="border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow duration-200 bg-white">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="font-semibold text-xl text-gray-900">{group.type_name}</h3>
                        <p className="text-sm text-gray-600 flex items-center gap-1">
                          <BarChart3 className="h-3 w-3" />
                          {group.operation_count} operations
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-gray-900">{formatCurrency(group.total_amount)}</div>
                        <div className="text-sm text-gray-600 bg-gray-100 px-2 py-1 rounded-full inline-block">
                          {((group.total_amount / reportData.total_amount) * 100).toFixed(1)}%
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-3">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleTypeGroupClick(group)}
                        className="flex items-center gap-2 border-gray-300 hover:bg-gray-50"
                      >
                        <Eye className="h-4 w-4" />
                        Top 10
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleShowAllOperations(group)}
                        className="flex items-center gap-2 border-gray-300 hover:bg-gray-50"
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
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="text-gray-800">
                  {typeOperations.type.name} - {selectedMonth}
                </CardTitle>
                <CardDescription className="text-gray-600">
                  {showAllOperations ? 'All operations' : 'Top 10 operations by amount'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-hidden rounded-lg border border-gray-200">
                  <Table>
                    <TableHeader>
                      <TableRow className="bg-gray-50">
                        <TableHead className="font-semibold text-gray-700">Date</TableHead>
                        <TableHead className="font-semibold text-gray-700">Description</TableHead>
                        <TableHead className="text-right font-semibold text-gray-700">Amount</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {typeOperations.operations.map((operation) => (
                        <TableRow key={operation.id} className="hover:bg-gray-50">
                          <TableCell className="font-medium text-gray-900">
                            {formatDate(operation.transaction_date)}
                          </TableCell>
                          <TableCell className="max-w-md">
                            <div className="truncate" title={operation.description}>
                              {operation.description}
                            </div>
                          </TableCell>
                          <TableCell className="text-right font-bold text-gray-900">
                            {formatCurrency(operation.amount_lei)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
                
                {typeOperations.pagination.has_more && !showAllOperations && (
                  <div className="mt-6 flex justify-center">
                    <Button
                      variant="outline"
                      onClick={() => fetchTypeOperations(
                        typeOperations.type.id,
                        typeOperations.pagination.limit,
                        typeOperations.pagination.offset + typeOperations.pagination.limit
                      )}
                      className="border-gray-300 hover:bg-gray-50"
                    >
                      Load More
                    </Button>
                  </div>
                )}
                
                <div className="mt-6 flex justify-end">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setSelectedTypeGroup(null)
                      setTypeOperations(null)
                      setShowAllOperations(false)
                    }}
                    className="border-gray-300 hover:bg-gray-50"
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
        <Card className="border-0 shadow-lg">
          <CardContent className="text-center py-16">
            <FileText className="h-16 w-16 mx-auto text-gray-300 mb-6" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No Data Available</h3>
            <p className="text-gray-500">
              No financial data found for the selected month.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
