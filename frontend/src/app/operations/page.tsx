'use client'

import { useState, useEffect } from 'react'
import { Activity, Plus, Edit, Trash2, Calendar } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { API_ENDPOINTS } from '@/lib/api'

interface Operation {
  id: number
  pdf_id: number
  type_id: number | null
  transaction_date: string | null
  processed_date: string | null
  description: string | null
  amount_lei: number | null
}

interface OperationType {
  id: number
  name: string
  description: string | null
  created_at: string | null
}

export default function OperationsPage() {
  const [operations, setOperations] = useState<Operation[]>([])
  const [operationTypes, setOperationTypes] = useState<OperationType[]>([])
  const [loading, setLoading] = useState(true)
  const [assignDialogOpen, setAssignDialogOpen] = useState(false)
  const [newTypeDialogOpen, setNewTypeDialogOpen] = useState(false)
  const [selectedOperation, setSelectedOperation] = useState<Operation | null>(null)
  const [selectedTypeId, setSelectedTypeId] = useState<string>('')
  const [newTypeName, setNewTypeName] = useState('')
  const [newTypeDescription, setNewTypeDescription] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  // Manual operation states
  const [manualOperationDialogOpen, setManualOperationDialogOpen] = useState(false)
  const [manualDate, setManualDate] = useState('')
  const [manualTime, setManualTime] = useState('')
  const [manualTypeId, setManualTypeId] = useState('')
  const [manualAmount, setManualAmount] = useState('')
  const [manualDescription, setManualDescription] = useState('')
  
  // Monthly operations states
  const [monthlyOperations, setMonthlyOperations] = useState<any[]>([])
  const [selectedMonth, setSelectedMonth] = useState('')
  const [monthlyOperationsLoading, setMonthlyOperationsLoading] = useState(false)
  const [deleteConfirmDialogOpen, setDeleteConfirmDialogOpen] = useState(false)
  const [operationToDelete, setOperationToDelete] = useState<any>(null)

  useEffect(() => {
    fetchOperations()
    fetchOperationTypes()
  }, [])

  const fetchOperations = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.OPERATIONS_NULL_TYPES)
      if (response.ok) {
        const data = await response.json()
        setOperations(data)
      }
    } catch (error) {
      console.error('Error fetching operations:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchOperationTypes = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.OPERATION_TYPES)
      if (response.ok) {
        const data = await response.json()
        setOperationTypes(data)
      }
    } catch (error) {
      console.error('Error fetching operation types:', error)
    }
  }

  const handleAssignType = async () => {
    if (!selectedOperation || !selectedTypeId) return

    setIsSubmitting(true)
    try {
      const response = await fetch(API_ENDPOINTS.ASSIGN_OPERATION_TYPE(selectedOperation.id), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `type_id=${selectedTypeId}`,
      })

      if (response.ok) {
        setAssignDialogOpen(false)
        setSelectedOperation(null)
        setSelectedTypeId('')
        fetchOperations() // Refresh the list
      }
    } catch (error) {
      console.error('Error assigning type:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCreateNewType = async () => {
    if (!newTypeName.trim()) return

    setIsSubmitting(true)
    try {
      const response = await fetch(API_ENDPOINTS.OPERATION_TYPES, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `name=${encodeURIComponent(newTypeName)}&description=${encodeURIComponent(newTypeDescription)}`,
      })

      if (response.ok) {
        const newType = await response.json()
        setOperationTypes([...operationTypes, newType])
        setNewTypeDialogOpen(false)
        setNewTypeName('')
        setNewTypeDescription('')
        
        // If we were in the assign dialog, set the new type as selected
        if (selectedOperation) {
          setSelectedTypeId(newType.id.toString())
        }
      }
    } catch (error) {
      console.error('Error creating operation type:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCreateManualOperation = async () => {
    if (!manualDate || !manualTime || !manualTypeId || !manualAmount) return

    setIsSubmitting(true)
    try {
      // Combine date and time and ensure proper format
      const transactionDate = `${manualDate}T${manualTime}:00`
      
      // Validate amount format (max 999999.99)
      const amount = parseFloat(manualAmount)
      if (isNaN(amount) || amount <= 0 || amount > 999999.99) {
        alert('Please enter a valid amount between 0.01 and 999999.99 MDL')
        setIsSubmitting(false)
        return
      }

      // Create form data
      const formData = new URLSearchParams()
      formData.append('transaction_date', transactionDate)
      formData.append('type_id', manualTypeId)
      formData.append('amount_lei', amount.toString())
      if (manualDescription) {
        formData.append('description', manualDescription)
      }



      const response = await fetch(API_ENDPOINTS.CREATE_MANUAL_OPERATION, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
      })

      if (response.ok) {
        const newOperation = await response.json()
        setManualOperationDialogOpen(false)
        // Reset form
        setManualDate('')
        setManualTime('')
        setManualTypeId('')
        setManualAmount('')
        setManualDescription('')
        
        // Refresh operations list to show the new manual operation
        fetchOperations()
      } else {
        try {
          const errorData = await response.json()
          if (response.status === 422) {
            // Handle validation errors
            if (errorData.detail && Array.isArray(errorData.detail)) {
              const errorMessages = errorData.detail.map((err: any) => 
                `${err.loc?.join('.')}: ${err.msg}`
              ).join(', ')
              alert(`Validation error: ${errorMessages}`)
            } else {
              alert(`Validation error: ${errorData.detail || 'Invalid data format'}`)
            }
          } else {
            alert(`Error creating manual operation: ${errorData.detail || 'Unknown error'}`)
          }
        } catch (parseError) {
          alert(`Error creating manual operation: ${response.statusText || 'Unknown error'}`)
        }
      }
    } catch (error) {
      console.error('Error creating manual operation:', error)
      alert('Error creating manual operation. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const openAssignDialog = (operation: Operation) => {
    setSelectedOperation(operation)
    setSelectedTypeId('')
    setAssignDialogOpen(true)
  }

  const fetchMonthlyOperations = async () => {
    if (!selectedMonth) return
    
    setMonthlyOperationsLoading(true)
    try {
      const [year, month] = selectedMonth.split('-').map(Number)
      console.log('Fetching operations for:', { year, month, selectedMonth })
      
      const response = await fetch(API_ENDPOINTS.OPERATIONS_BY_MONTH(year, month))
      console.log('Response status:', response.status)
      
      if (response.ok) {
        const data = await response.json()
        console.log('Received operations:', data)
        setMonthlyOperations(data)
      } else {
        console.error('Error fetching monthly operations:', response.statusText)
        const errorText = await response.text()
        console.error('Error response:', errorText)
      }
    } catch (error) {
      console.error('Error fetching monthly operations:', error)
    } finally {
      setMonthlyOperationsLoading(false)
    }
  }

  const handleDeleteOperation = async (operation: any) => {
    setOperationToDelete(operation)
    setDeleteConfirmDialogOpen(true)
  }

  const confirmDeleteOperation = async () => {
    if (!operationToDelete) return

    setIsSubmitting(true)
    try {
      const response = await fetch(API_ENDPOINTS.DELETE_OPERATION(operationToDelete.id), {
        method: 'DELETE',
      })

      if (response.ok) {
        setDeleteConfirmDialogOpen(false)
        setOperationToDelete(null)
        // Refresh the monthly operations list
        fetchMonthlyOperations()
        // Also refresh the null types operations list
        fetchOperations()
      } else {
        const errorData = await response.json()
        alert(`Error deleting operation: ${errorData.detail || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Error deleting operation:', error)
      alert('Error deleting operation. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString()
  }

  const formatAmount = (amount: number | null) => {
    if (amount === null) return '-'
    return new Intl.NumberFormat('md-MD', {
      style: 'currency',
      currency: 'MDL'
    }).format(amount)
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="text-center py-12">
          <Activity className="h-12 w-12 mx-auto text-muted-foreground mb-4 animate-spin" />
          <p className="text-muted-foreground">Loading operations...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Operations</h1>
        <p className="text-muted-foreground">
          Manage operations that need type assignment from your PDF statements.
        </p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Operations Without Types ({operations.length})
          </CardTitle>
          <CardDescription>
            These operations need to be categorized. Select an existing type or create a new one.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {operations.length === 0 ? (
            <div className="text-center py-12">
              <Activity className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No Operations Without Types</h3>
              <p className="text-muted-foreground">
                All operations have been properly categorized.
              </p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {operations.map((operation) => (
                  <TableRow key={operation.id}>
                    <TableCell>
                      {formatDate(operation.transaction_date)}
                    </TableCell>
                    <TableCell className="max-w-md truncate">
                      {operation.description || '-'}
                    </TableCell>
                    <TableCell>
                      {formatAmount(operation.amount_lei)}
                    </TableCell>
                    <TableCell>
                      <Button
                        size="sm"
                        onClick={() => openAssignDialog(operation)}
                        className="flex items-center gap-2"
                      >
                        <Edit className="h-4 w-4" />
                        Assign Type
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Manual Operations Section */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Plus className="h-5 w-5" />
            Add Manual Operation
          </CardTitle>
          <CardDescription>
            Add operations manually that are not from PDF files. These will be included in all reports.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            onClick={() => setManualOperationDialogOpen(true)}
            className="flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Add Manual Operation
          </Button>
        </CardContent>
      </Card>

      {/* Monthly Operations Section */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Monthly Operations
          </CardTitle>
          <CardDescription>
            View and manage operations for a specific month. You can delete operations from here.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-6">
            <div className="flex-1">
              <Label htmlFor="month-select">Select Month</Label>
              <Input
                id="month-select"
                type="month"
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(e.target.value)}
                className="mt-1"
              />
            </div>
            <div className="flex items-end">
              <Button
                onClick={fetchMonthlyOperations}
                disabled={!selectedMonth || monthlyOperationsLoading}
                className="flex items-center gap-2"
              >
                {monthlyOperationsLoading ? (
                  <Activity className="h-4 w-4 animate-spin" />
                ) : (
                  <Calendar className="h-4 w-4" />
                )}
                {monthlyOperationsLoading ? 'Loading...' : 'Load Operations'}
              </Button>
            </div>
          </div>

          {monthlyOperations.length > 0 && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium">
                  Operations for {selectedMonth} ({monthlyOperations.length})
                </h3>
              </div>
              
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Source</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {monthlyOperations.map((operation) => (
                    <TableRow key={operation.id}>
                      <TableCell>
                        {formatDate(operation.transaction_date)}
                      </TableCell>
                      <TableCell>
                        {operation.type_name || 'No Type'}
                      </TableCell>
                      <TableCell className="max-w-md truncate">
                        {operation.description || '-'}
                      </TableCell>
                      <TableCell>
                        {formatAmount(operation.amount_lei)}
                      </TableCell>
                      <TableCell>
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          operation.is_manual 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {operation.is_manual ? 'Manual' : 'PDF'}
                        </span>
                      </TableCell>
                      <TableCell>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleDeleteOperation(operation)}
                          className="flex items-center gap-2"
                        >
                          <Trash2 className="h-4 w-4" />
                          Delete
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}

          {selectedMonth && monthlyOperations.length === 0 && !monthlyOperationsLoading && (
            <div className="text-center py-8">
              <Calendar className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No Operations Found</h3>
              <p className="text-muted-foreground">
                No operations found for {selectedMonth}.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Assign Type Dialog */}
      <Dialog open={assignDialogOpen} onOpenChange={setAssignDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Assign Operation Type</DialogTitle>
            <DialogDescription>
              Select an existing type or create a new one for this operation.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="type-select">Select Type</Label>
              <Select value={selectedTypeId} onValueChange={setSelectedTypeId}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose a type..." />
                </SelectTrigger>
                <SelectContent>
                  {operationTypes.map((type) => (
                    <SelectItem key={type.id} value={type.id.toString()}>
                      {type.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center gap-2">
              <div className="flex-1 h-px bg-border" />
              <span className="text-sm text-muted-foreground">or</span>
              <div className="flex-1 h-px bg-border" />
            </div>

            <Button
              variant="outline"
              onClick={() => setNewTypeDialogOpen(true)}
              className="w-full"
            >
              <Plus className="h-4 w-4 mr-2" />
              Create New Type
            </Button>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setAssignDialogOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              onClick={handleAssignType}
              disabled={!selectedTypeId || isSubmitting}
            >
              {isSubmitting ? 'Assigning...' : 'Assign Type'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Create New Type Dialog */}
      <Dialog open={newTypeDialogOpen} onOpenChange={setNewTypeDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Operation Type</DialogTitle>
            <DialogDescription>
              Add a new category for operations.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="type-name">Type Name</Label>
              <Input
                id="type-name"
                value={newTypeName}
                onChange={(e) => setNewTypeName(e.target.value)}
                placeholder="e.g., Groceries, Utilities, Entertainment"
              />
            </div>
            
            <div>
              <Label htmlFor="type-description">Description (Optional)</Label>
              <Input
                id="type-description"
                value={newTypeDescription}
                onChange={(e) => setNewTypeDescription(e.target.value)}
                placeholder="Brief description of this type"
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setNewTypeDialogOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              onClick={handleCreateNewType}
              disabled={!newTypeName.trim() || isSubmitting}
            >
              {isSubmitting ? 'Creating...' : 'Create Type'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Manual Operation Dialog */}
      <Dialog open={manualOperationDialogOpen} onOpenChange={setManualOperationDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Manual Operation</DialogTitle>
            <DialogDescription>
              Add a new operation manually. This will be stored without a PDF file and included in all reports.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="manual-date">Date</Label>
                <Input
                  id="manual-date"
                  type="date"
                  value={manualDate}
                  onChange={(e) => setManualDate(e.target.value)}
                  required
                />
              </div>
              <div>
                <Label htmlFor="manual-time">Time</Label>
                <Input
                  id="manual-time"
                  type="time"
                  value={manualTime}
                  onChange={(e) => setManualTime(e.target.value)}
                  required
                />
              </div>
            </div>

            <div>
              <Label htmlFor="manual-type">Operation Type</Label>
              <Select value={manualTypeId} onValueChange={setManualTypeId}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose a type..." />
                </SelectTrigger>
                <SelectContent>
                  {operationTypes.map((type) => (
                    <SelectItem key={type.id} value={type.id.toString()}>
                      {type.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="manual-amount">Amount (MDL)</Label>
              <Input
                id="manual-amount"
                type="number"
                step="0.01"
                min="0.01"
                max="999999.99"
                value={manualAmount}
                onChange={(e) => setManualAmount(e.target.value)}
                placeholder="0.00"
                required
              />
              <p className="text-sm text-muted-foreground mt-1">
                Maximum amount: 999,999.99 MDL
              </p>
            </div>

            <div>
              <Label htmlFor="manual-description">Description (Optional)</Label>
              <Input
                id="manual-description"
                value={manualDescription}
                onChange={(e) => setManualDescription(e.target.value)}
                placeholder="Brief description of the operation"
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setManualOperationDialogOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              onClick={handleCreateManualOperation}
              disabled={!manualDate || !manualTime || !manualTypeId || !manualAmount || isSubmitting}
            >
              {isSubmitting ? 'Creating...' : 'Create Operation'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmDialogOpen} onOpenChange={setDeleteConfirmDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Delete Operation</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this operation? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          
          {operationToDelete && (
            <div className="space-y-2 p-4 bg-muted rounded-lg">
              <p><strong>Date:</strong> {formatDate(operationToDelete.transaction_date)}</p>
              <p><strong>Type:</strong> {operationToDelete.type_name || 'No Type'}</p>
              <p><strong>Description:</strong> {operationToDelete.description || '-'}</p>
              <p><strong>Amount:</strong> {formatAmount(operationToDelete.amount_lei)}</p>
              <p><strong>Source:</strong> {operationToDelete.is_manual ? 'Manual' : 'PDF'}</p>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteConfirmDialogOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={confirmDeleteOperation}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Deleting...' : 'Delete Operation'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
