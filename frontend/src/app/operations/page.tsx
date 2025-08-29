import { Activity } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function OperationsPage() {
  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Operations</h1>
        <p className="text-muted-foreground">
          View and manage financial operations from your PDF statements.
        </p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Operations Management
          </CardTitle>
          <CardDescription>
            This page will display detailed operations data from your financial statements.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <Activity className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">Operations Page</h3>
            <p className="text-muted-foreground">
              This section will be updated to show detailed operations data, 
              including transaction types, amounts, and categorization.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
