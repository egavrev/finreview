'use client'

import { useState, useEffect } from 'react'
import { Upload, FileText, Trash2, AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
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
  operations_count: number
}

export default function FilesPage() {
  const [pdfs, setPdfs] = useState<PDF[]>([])
  const [uploading, setUploading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadResult, setUploadResult] = useState<any>(null)
  const [deleting, setDeleting] = useState<number | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<number | null>(null)

  useEffect(() => {
    fetchPDFs()
  }, [])

  const fetchPDFs = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.PDFS)
      const data = await response.json()
      setPdfs(data)
    } catch (error) {
      console.error('Error fetching PDFs:', error)
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
    setUploadResult(null)
    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await fetch(API_ENDPOINTS.UPLOAD_PDF, {
        method: 'POST',
        body: formData,
      })

      if (response.ok) {
        const result = await response.json()
        console.log('Upload successful:', result)
        setUploadResult(result)
        setSelectedFile(null)
        fetchPDFs()
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

  const handleDeleteClick = (pdfId: number) => {
    setShowDeleteConfirm(pdfId)
  }

  const handleDeleteConfirm = async (pdfId: number) => {
    setDeleting(pdfId)
    setShowDeleteConfirm(null)

    try {
      const response = await fetch(API_ENDPOINTS.DELETE_PDF(pdfId), {
        method: 'DELETE',
      })

      if (response.ok) {
        const result = await response.json()
        console.log('Delete successful:', result)
        fetchPDFs()
        // Clear upload result if it was for the deleted PDF
        if (uploadResult && uploadResult.pdf_id === pdfId) {
          setUploadResult(null)
        }
      } else {
        const error = await response.json()
        alert(`Delete failed: ${error.detail}`)
      }
    } catch (error) {
      console.error('Delete error:', error)
      alert('Delete failed. Please try again.')
    } finally {
      setDeleting(null)
    }
  }

  const handleDeleteCancel = () => {
    setShowDeleteConfirm(null)
  }

  return (
    <div className="p-8 space-y-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Files</h1>
        <p className="text-muted-foreground">
          Upload and manage your PDF financial statements.
        </p>
      </div>
      
      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Upload PDF
          </CardTitle>
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

      {/* Upload Results */}
      {uploadResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Upload Results
            </CardTitle>
            <CardDescription>Processing results and deduplication information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-semibold text-green-800">Operations Stored</h3>
                <p className="text-2xl font-bold text-green-600">{uploadResult.operations_stored}</p>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <h3 className="font-semibold text-yellow-800">Operations Skipped (Duplicates)</h3>
                <p className="text-2xl font-bold text-yellow-600">{uploadResult.operations_skipped}</p>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-blue-800">Total Processed</h3>
                <p className="text-2xl font-bold text-blue-600">{uploadResult.total_operations_processed}</p>
              </div>
            </div>
            
            {uploadResult.deduplication_info.duplicates_found && (
              <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                <h3 className="font-semibold text-orange-800 mb-2">Duplicate Detection</h3>
                <p className="text-orange-700">
                  Found {uploadResult.operations_skipped} duplicate operations ({uploadResult.deduplication_info.duplicate_percentage.toFixed(1)}% of total)
                </p>
                <p className="text-sm text-orange-600 mt-1">
                  Duplicates were automatically skipped to prevent data redundancy.
                </p>
              </div>
            )}
            
            {uploadResult.pdf_summary && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-2">PDF Summary</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Client:</span> {uploadResult.pdf_summary.client_name || 'N/A'}
                  </div>
                  <div>
                    <span className="text-gray-600">Account:</span> {uploadResult.pdf_summary.account_number || 'N/A'}
                  </div>
                  <div>
                    <span className="text-gray-600">Initial Balance:</span> {uploadResult.pdf_summary.sold_initial?.toFixed(2) || 'N/A'} LEI
                  </div>
                  <div>
                    <span className="text-gray-600">Final Balance:</span> {uploadResult.pdf_summary.sold_final?.toFixed(2) || 'N/A'} LEI
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Uploaded Files */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Uploaded Files ({pdfs.length})
          </CardTitle>
          <CardDescription>Manage your uploaded PDF files and their associated operations</CardDescription>
        </CardHeader>
        <CardContent>
          {pdfs.length === 0 ? (
            <p className="text-sm text-muted-foreground">No files uploaded yet.</p>
          ) : (
            <div className="space-y-4">
              {pdfs.map((pdf) => (
                <div key={pdf.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-medium text-gray-900">
                          {pdf.client_name || 'Unknown Client'}
                        </h3>
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {pdf.operations_count} operations
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">
                        Account: {pdf.account_number || 'N/A'}
                      </p>
                      <p className="text-sm text-gray-500">
                        File: {pdf.file_path.split('/').pop()}
                      </p>
                      <div className="flex gap-4 mt-2 text-xs text-gray-500">
                        <span>Initial: {pdf.sold_initial?.toFixed(2) || 'N/A'} LEI</span>
                        <span>Final: {pdf.sold_final?.toFixed(2) || 'N/A'} LEI</span>
                        <span>Total Out: {pdf.total_iesiri?.toFixed(2) || 'N/A'} LEI</span>
                        <span className="font-medium text-blue-600">Operations: {pdf.operations_count}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {showDeleteConfirm === pdf.id ? (
                        <div className="flex items-center gap-2 bg-red-50 p-2 rounded-lg border border-red-200">
                          <AlertTriangle className="h-4 w-4 text-red-600" />
                          <span className="text-sm text-red-700">Delete this file?</span>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleDeleteConfirm(pdf.id!)}
                            disabled={deleting === pdf.id}
                          >
                            {deleting === pdf.id ? 'Deleting...' : 'Yes'}
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={handleDeleteCancel}
                            disabled={deleting === pdf.id}
                          >
                            No
                          </Button>
                        </div>
                      ) : (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteClick(pdf.id!)}
                          disabled={deleting === pdf.id}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Upload Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Upload Status
          </CardTitle>
          <CardDescription>Track your uploaded files and processing status</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Total files uploaded: {pdfs.length}
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            View all processed PDFs on the <a href="/" className="text-blue-600 hover:underline">Dashboard</a>.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
