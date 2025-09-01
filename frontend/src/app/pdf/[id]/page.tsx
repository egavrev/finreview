'use client'

import { useState, useEffect } from 'react'
import { ArrowLeft, Calendar, DollarSign, FileText } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { API_ENDPOINTS } from '@/lib/api'

interface PDF {
  id: number
  file_path: string
  client_name: string | null
  account_number: string | null
  total_iesiri: number | null
  sold_initial: number | null
  sold_final: number | null
  created_at: string | null
}

interface Operation {
  id: number
  pdf_id: number
  transaction_date: string | null
  processed_date: string | null
  description: string | null
  amount_lei: number | null
}

interface PDFDetails {
  pdf: PDF
  operations: Operation[]
}

export default function PDFDetailsPage({ params }: { params: { id: string } }) {
  const [pdfDetails, setPdfDetails] = useState<PDFDetails | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchPDFDetails()
  }, [params.id])

  const fetchPDFDetails = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.PDF_BY_ID(Number(params.id)))
      if (response.ok) {
        const data = await response.json()
        setPdfDetails(data)
      } else {
        console.error('Failed to fetch PDF details')
      }
    } catch (error) {
      console.error('Error fetching PDF details:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number | null) => {
    if (amount === null) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'MDL',
    }).format(amount)
  }

  const formatDate = (date: string | null) => {
    if (!date) return 'N/A'
    return new Date(date).toLocaleDateString()
  }

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Loading...</div>
        </div>
      </div>
    )
  }

  if (!pdfDetails) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg text-red-600">PDF not found</div>
        </div>
      </div>
    )
  }

  const { pdf, operations } = pdfDetails

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Link href="/">
          <Button variant="outline" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold">PDF Details</h1>
          <p className="text-muted-foreground">Financial statement analysis</p>
        </div>
      </div>

      {/* PDF Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Client</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{pdf.client_name || 'N/A'}</div>
            <p className="text-xs text-muted-foreground">{pdf.account_number || 'No account number'}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Iesiri</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(pdf.total_iesiri)}</div>
            <p className="text-xs text-muted-foreground">Total withdrawals</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Balance Range</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-sm">
              <div>Initial: {formatCurrency(pdf.sold_initial)}</div>
              <div>Final: {formatCurrency(pdf.sold_final)}</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Operations Table */}
      <Card>
        <CardHeader>
          <CardTitle>Operations ({operations.length})</CardTitle>
          <CardDescription>Detailed list of all financial operations</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Processed</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Amount</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {operations.map((operation) => (
                <TableRow key={operation.id}>
                  <TableCell>{formatDate(operation.transaction_date)}</TableCell>
                  <TableCell>{formatDate(operation.processed_date)}</TableCell>
                  <TableCell className="max-w-md truncate">
                    {operation.description || 'N/A'}
                  </TableCell>
                  <TableCell className={operation.amount_lei && operation.amount_lei < 0 ? 'text-red-600' : 'text-green-600'}>
                    {formatCurrency(operation.amount_lei)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
