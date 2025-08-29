'use client'

import { useState, useEffect } from 'react'
import { Upload, FileText, BarChart3, DollarSign, TrendingUp } from 'lucide-react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

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

interface Statistics {
  total_pdfs: number
  total_operations: number
  total_iesiri: number
  total_amount: number
  average_amount_per_operation: number
}

const API_BASE = 'http://localhost:8000'

export default function Dashboard() {
  const [pdfs, setPdfs] = useState<PDF[]>([])
  const [statistics, setStatistics] = useState<Statistics | null>(null)
  const [uploading, setUploading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  useEffect(() => {
    fetchPDFs()
    fetchStatistics()
  }, [])

  const fetchPDFs = async () => {
    try {
      const response = await fetch(`${API_BASE}/pdfs`)
      const data = await response.json()
      setPdfs(data)
    } catch (error) {
      console.error('Error fetching PDFs:', error)
    }
  }

  const fetchStatistics = async () => {
    try {
      const response = await fetch(`${API_BASE}/statistics`)
      const data = await response.json()
      setStatistics(data)
    } catch (error) {
      console.error('Error fetching statistics:', error)
    }
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await fetch(`${API_BASE}/upload-pdf`, {
        method: 'POST',
        body: formData,
      })

      if (response.ok) {
        const result = await response.json()
        console.log('Upload successful:', result)
        setSelectedFile(null)
        fetchPDFs()
        fetchStatistics()
      } else {
        const error = await response.json()
        alert(`Upload failed: ${error.detail}`)
      }
    } catch (error) {
      console.error('Upload error:', error)
      alert('Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const formatCurrency = (amount: number | null) => {
    if (amount === null) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'MDL',
    }).format(amount)
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Financial Review Dashboard</h1>
          <p className="text-muted-foreground">Upload and analyze PDF financial statements</p>
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

      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle>Upload PDF</CardTitle>
          <CardDescription>Upload a PDF financial statement to process and analyze</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-4">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              className="flex-1"
            />
            <Button 
              onClick={handleUpload} 
              disabled={!selectedFile || uploading}
              className="flex items-center space-x-2"
            >
              <Upload className="h-4 w-4" />
              {uploading ? 'Uploading...' : 'Upload'}
            </Button>
          </div>
          {selectedFile && (
            <p className="text-sm text-muted-foreground">
              Selected: {selectedFile.name}
            </p>
          )}
        </CardContent>
      </Card>

      {/* PDFs Table */}
      <Card>
        <CardHeader>
          <CardTitle>Processed PDFs</CardTitle>
          <CardDescription>List of all processed financial statements</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Client</TableHead>
                <TableHead>Account</TableHead>
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
  )
}
