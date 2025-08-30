'use client'

import { useState, useEffect } from 'react'
import { Activity, Plus, Edit } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'

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

  useEffect(() => {
    fetchOperations()
    fetchOperationTypes()
  }, [])

  const fetchOperations = async () => {
    try {
      const response = await fetch('http://localhost:8000/operations/null-types')
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
      const response = await fetch('http://localhost:8000/operation-types')
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
      const response = await fetch(`http://localhost:8000/operations/${selectedOperation.id}/assign-type`, {
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
      const response = await fetch('http://localhost:8000/operation-types', {
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

  const openAssignDialog = (operation: Operation) => {
    setSelectedOperation(operation)
    setSelectedTypeId('')
    setAssignDialogOpen(true)
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
              <Select
                id="type-select"
                value={selectedTypeId}
                onChange={(e) => setSelectedTypeId(e.target.value)}
              >
                <option value="">Choose a type...</option>
                {operationTypes.map((type) => (
                  <option key={type.id} value={type.id}>
                    {type.name}
                  </option>
                ))}
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
    </div>
  )
}
