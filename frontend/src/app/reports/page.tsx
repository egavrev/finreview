'use client'

import { useState, useEffect } from 'react'
import { FileText, Calendar, PieChart, BarChart3, Eye, ChevronRight, Clock, TrendingUp } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { PieChart as RechartsPieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { format, parseISO } from 'date-fns'
import { API_ENDPOINTS } from '@/lib/api'

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
      const response = await fetch(API_ENDPOINTS.AVAILABLE_MONTHS)
      if (response.ok) {
        const months = await response.json()
        setAvailableMonths(months)
        if (months.length > 0) {
          setSelectedMonth(months[0].label)
        }
      } else {
        // Handle non-ok response
        setAvailableMonths([])
        console.error('Failed to fetch available months:', response.status)
      }
    } catch (error) {
      console.error('Error fetching available months:', error)
      setAvailableMonths([])
    }
  }

  const fetchMonthlyReport = async () => {
    if (!selectedMonth) return
    
    setLoading(true)
    try {
      const [year, month] = selectedMonth.split('-').map(Number)
      const response = await fetch(API_ENDPOINTS.MONTHLY_REPORT(year, month))
      if (response.ok) {
        const data = await response.json()
        setReportData(data)
      } else {
        // Handle non-ok response
        setReportData(null)
        console.error('Failed to fetch monthly report:', response.status)
      }
    } catch (error) {
      console.error('Error fetching monthly report:', error)
      setReportData(null)
    } finally {
      setLoading(false)
    }
  }

  const fetchTypeOperations = async (typeId: number, limit: number = 10, offset: number = 0, append: boolean = false) => {
    if (!selectedMonth || !typeId) return
    
    try {
      const [year, month] = selectedMonth.split('-').map(Number)
      const response = await fetch(
        API_ENDPOINTS.MONTHLY_OPERATIONS_BY_TYPE(year, month, typeId) + `?limit=${limit}&offset=${offset}`
      )
      if (response.ok) {
        const data = await response.json()
        if (append && typeOperations) {
          // Append new operations to existing ones
          setTypeOperations({
            ...data,
            operations: [...typeOperations.operations, ...data.operations]
          })
        } else {
          setTypeOperations(data)
        }
      } else {
        // Handle non-ok response
        console.error('Failed to fetch type operations:', response.status)
        if (!append) {
          setTypeOperations(null)
        }
      }
    } catch (error) {
      console.error('Error fetching type operations:', error)
      if (!append) {
        setTypeOperations(null)
      }
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
          // Load only top 5 operations initially
          fetchTypeOperations(typeGroup.type_id, 5, 0)
        }
      }
    }
  }

  const handleTypeGroupClick = (group: TypeGroup) => {
    setSelectedTypeGroup(group)
    setSelectedPieSlice(group.type_name)
    if (group.type_id) {
      // Load only top 5 operations initially
      fetchTypeOperations(group.type_id, 5, 0)
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
            const percentage = ((entry.payload.value / reportData.total_amount) * 100).toFixed(1)
            const isSelected = selectedPieSlice === entry.name
            return (
              <div
                key={index}
                className={`flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-all duration-200 ${
                  isSelected 
                    ? 'bg-blue-50 border border-blue-200' 
                    : 'hover:bg-gray-50'
                }`}
                onClick={() => handlePieSliceClick({ name: entry.name })}
              >
                <div 
                  className="w-3 h-3 rounded-full flex-shrink-0" 
                  style={{ backgroundColor: entry.color }}
                />
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {entry.name}
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
      {/* Compact Header with Title and Month Selection */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
            Financial Reports
          </h1>
          <p className="text-muted-foreground">
            Generate and view comprehensive financial reports and analytics by month.
          </p>
        </div>
        <div className="flex items-center gap-4">
          <Select value={selectedMonth} onValueChange={setSelectedMonth}>
            <SelectTrigger className="w-48 border-gray-300 focus:border-blue-500 focus:ring-blue-500">
              <Calendar className="h-4 w-4 mr-2" />
              <SelectValue placeholder="Select month" />
            </SelectTrigger>
            <SelectContent>
              {availableMonths && availableMonths.length > 0 ? (
                availableMonths.map((month) => (
                  <SelectItem key={month.label} value={month.label}>
                    {month.label}
                  </SelectItem>
                ))
              ) : (
                <SelectItem value="no-data" disabled>
                  No months available
                </SelectItem>
              )}
            </SelectContent>
          </Select>
          {loading && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              Loading...
            </div>
          )}
        </div>
      </div>

      {/* Monthly Report */}
      {reportData && (
        <>
          {/* Compact Stats Row */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-800">Total Amount</span>
              </div>
              <div className="text-xl font-bold text-blue-900">{formatCurrency(reportData.total_amount)}</div>
            </div>
            <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
              <div className="flex items-center gap-2 mb-1">
                <BarChart3 className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium text-green-800">Total Operations</span>
              </div>
              <div className="text-xl font-bold text-green-900">{reportData.total_operations}</div>
            </div>
            <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
              <div className="flex items-center gap-2 mb-1">
                <PieChart className="h-4 w-4 text-purple-600" />
                <span className="text-sm font-medium text-purple-800">Average per Op</span>
              </div>
              <div className="text-xl font-bold text-purple-900">
                {formatCurrency(reportData.summary.average_amount_per_operation)}
              </div>
            </div>
            <div className="bg-gradient-to-r from-orange-50 to-orange-100 rounded-lg p-4 border border-orange-200">
              <div className="flex items-center gap-2 mb-1">
                <FileText className="h-4 w-4 text-orange-600" />
                <span className="text-sm font-medium text-orange-800">Largest Category</span>
              </div>
              <div className="text-lg font-bold text-orange-900">
                {reportData.summary.most_expensive_type || 'N/A'}
              </div>
              <div className="text-sm text-orange-700">
                {formatCurrency(reportData.summary.most_expensive_amount)}
              </div>
            </div>
          </div>

          {/* Main Pie Chart Section */}
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
                    name: entry.name,
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



          {/* Type Operations Modal/Dialog */}
          {selectedTypeGroup && typeOperations && (
            <Card className="border-0 shadow-lg">
              <CardHeader>
                <CardTitle className="text-gray-800">
                  {typeOperations.type.name} - {selectedMonth}
                </CardTitle>
                <CardDescription className="text-gray-600">
                  {showAllOperations ? 'All operations' : 'Top 5 operations by amount'}
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
                      onClick={() => {
                        // Load all remaining operations at once and append them
                        const remainingCount = typeOperations.pagination.total - typeOperations.operations.length
                        fetchTypeOperations(
                          typeOperations.type.id,
                          remainingCount,
                          typeOperations.operations.length,
                          true // append = true
                        )
                      }}
                      className="border-gray-300 hover:bg-gray-50"
                    >
                      Load All Remaining ({typeOperations.pagination.total - typeOperations.operations.length})
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
