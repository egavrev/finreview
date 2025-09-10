'use client'

import { useState, useEffect } from 'react'
import { FileText, BarChart3, DollarSign, TrendingUp } from 'lucide-react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { API_ENDPOINTS } from '@/lib/api'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { useAuth } from '@/contexts/AuthContext'

interface Statistics {
  total_pdfs: number
  total_operations: number
  total_iesiri: number
  total_amount: number
  average_amount_per_operation: number
}

interface PDF {
  id: number
  file_path: string
  client_name: string | null
  account_number: string | null
  total_iesiri: number | null
  sold_initial: number | null
  sold_final: number | null
  created_at: string | null
  operations_count: number
}

export const formatCurrency = (amount: number | null) => {
  if (amount === null) return 'N/A'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'MDL',
  }).format(amount)
}

export default function Dashboard() {
  const [statistics, setStatistics] = useState<Statistics | null>(null)
  const [pdfs, setPdfs] = useState<PDF[]>([])
  const { token } = useAuth()

  useEffect(() => {
    if (token) {
      fetchStatistics()
      fetchPDFs()
    }
  }, [token])

  const fetchStatistics = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.STATISTICS, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      const data = await response.json()
      setStatistics(data)
    } catch (error) {
      console.error('Error fetching statistics:', error)
    }
  }

  const fetchPDFs = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.PDFS, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      const data = await response.json()
      setPdfs(data)
    } catch (error) {
      console.error('Error fetching PDFs:', error)
    }
  }

  return (
    <ProtectedRoute>
      <div className="p-8 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-muted-foreground">Overview of your financial data and statistics</p>
          </div>
        </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total PDFs</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.total_pdfs}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Operations</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.total_operations}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Iesiri</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(statistics.total_iesiri)}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg per Operation</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(statistics.average_amount_per_operation)}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Processed PDFs Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Processed PDFs
          </CardTitle>
          <CardDescription>List of all processed financial statements</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Client</TableHead>
                <TableHead>Account</TableHead>
                <TableHead>Operations</TableHead>
                <TableHead>Total Iesiri</TableHead>
                <TableHead>Initial Balance</TableHead>
                <TableHead>Final Balance</TableHead>
                <TableHead>File</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {pdfs.map((pdf) => (
                <TableRow key={pdf.id}>
                  <TableCell>{pdf.id}</TableCell>
                  <TableCell>{pdf.client_name || 'N/A'}</TableCell>
                  <TableCell>{pdf.account_number || 'N/A'}</TableCell>
                  <TableCell>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {pdf.operations_count}
                    </span>
                  </TableCell>
                  <TableCell>{formatCurrency(pdf.total_iesiri)}</TableCell>
                  <TableCell>{formatCurrency(pdf.sold_initial)}</TableCell>
                  <TableCell>{formatCurrency(pdf.sold_final)}</TableCell>
                  <TableCell>
                    <Link href={`/pdf/${pdf.id}`} className="text-blue-600 hover:underline">
                      View Details
                    </Link>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      </div>
    </ProtectedRoute>
  )
}
