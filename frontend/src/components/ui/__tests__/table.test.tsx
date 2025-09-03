import React from 'react'
import { render, screen } from '../../../lib/test-utils'
import {
  Table,
  TableHeader,
  TableBody,
  TableFooter,
  TableHead,
  TableRow,
  TableCell,
  TableCaption,
} from '../table'

describe('Table Components', () => {
  describe('Table Component', () => {
    it('should render table with default props', () => {
      render(
        <Table>
          <tbody>
            <tr>
              <td>Table Content</td>
            </tr>
          </tbody>
        </Table>
      )
      const table = screen.getByRole('table')
      expect(table).toBeInTheDocument()
      expect(table).toHaveClass('w-full', 'caption-bottom', 'text-sm')
    })

    it('should render table with custom className', () => {
      render(
        <Table className="custom-table">
          <tbody>
            <tr>
              <td>Custom Table</td>
            </tr>
          </tbody>
        </Table>
      )
      const table = screen.getByRole('table')
      expect(table).toHaveClass('custom-table')
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLTableElement>()
      render(
        <Table ref={ref}>
          <tbody>
            <tr>
              <td>Ref Table</td>
            </tr>
          </tbody>
        </Table>
      )
      expect(ref.current).toBeInstanceOf(HTMLTableElement)
    })

    it('should forward HTML attributes', () => {
      render(
        <Table data-testid="test-table" id="table-1">
          <tbody>
            <tr>
              <td>Test Table</td>
            </tr>
          </tbody>
        </Table>
      )
      const table = screen.getByTestId('test-table')
      expect(table).toHaveAttribute('id', 'table-1')
    })

    it('should wrap table in overflow container', () => {
      render(
        <Table>
          <tbody>
            <tr>
              <td>Overflow Table</td>
            </tr>
          </tbody>
        </Table>
      )
      const container = screen.getByRole('table').parentElement
      expect(container).toHaveClass('relative', 'w-full', 'overflow-auto')
    })
  })

  describe('TableHeader Component', () => {
    it('should render table header with default props', () => {
      render(
        <Table>
          <TableHeader>
            <tr>
              <th>Header</th>
            </tr>
          </TableHeader>
        </Table>
      )
      const header = screen.getByRole('rowgroup')
      expect(header).toBeInTheDocument()
      expect(header).toHaveClass('[&_tr]:border-b')
    })

    it('should render table header with custom className', () => {
      render(
        <Table>
          <TableHeader className="custom-header">
            <tr>
              <th>Custom Header</th>
            </tr>
          </TableHeader>
        </Table>
      )
      const header = screen.getByRole('rowgroup')
      expect(header).toHaveClass('custom-header')
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLTableSectionElement>()
      render(
        <Table>
          <TableHeader ref={ref}>
            <tr>
              <th>Ref Header</th>
            </tr>
          </TableHeader>
        </Table>
      )
      expect(ref.current).toBeInstanceOf(HTMLTableSectionElement)
    })

    it('should forward HTML attributes', () => {
      render(
        <Table>
          <TableHeader data-testid="test-header" id="header-1">
            <tr>
              <th>Test Header</th>
            </tr>
          </TableHeader>
        </Table>
      )
      const header = screen.getByTestId('test-header')
      expect(header).toHaveAttribute('id', 'header-1')
    })
  })

  describe('TableBody Component', () => {
    it('should render table body with default props', () => {
      render(
        <Table>
          <TableBody>
            <tr>
              <td>Body Content</td>
            </tr>
          </TableBody>
        </Table>
      )
      const body = screen.getByRole('rowgroup')
      expect(body).toBeInTheDocument()
      expect(body).toHaveClass('[&_tr:last-child]:border-0')
    })

    it('should render table body with custom className', () => {
      render(
        <Table>
          <TableBody className="custom-body">
            <tr>
              <td>Custom Body</td>
            </tr>
          </TableBody>
        </Table>
      )
      const body = screen.getByRole('rowgroup')
      expect(body).toHaveClass('custom-body')
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLTableSectionElement>()
      render(
        <Table>
          <TableBody ref={ref}>
            <tr>
              <td>Ref Body</td>
            </tr>
          </TableBody>
        </Table>
      )
      expect(ref.current).toBeInstanceOf(HTMLTableSectionElement)
    })

    it('should forward HTML attributes', () => {
      render(
        <Table>
          <TableBody data-testid="test-body" id="body-1">
            <tr>
              <td>Test Body</td>
            </tr>
          </TableBody>
        </Table>
      )
      const body = screen.getByTestId('test-body')
      expect(body).toHaveAttribute('id', 'body-1')
    })
  })

  describe('TableFooter Component', () => {
    it('should render table footer with default props', () => {
      render(
        <Table>
          <TableFooter>
            <tr>
              <td>Footer Content</td>
            </tr>
          </TableFooter>
        </Table>
      )
      const footer = screen.getByRole('rowgroup')
      expect(footer).toBeInTheDocument()
      expect(footer).toHaveClass(
        'border-t',
        'bg-muted/50',
        'font-medium',
        '[&>tr]:last:border-b-0'
      )
    })

    it('should render table footer with custom className', () => {
      render(
        <Table>
          <TableFooter className="custom-footer">
            <tr>
              <td>Custom Footer</td>
            </tr>
          </TableFooter>
        </Table>
      )
      const footer = screen.getByRole('rowgroup')
      expect(footer).toHaveClass('custom-footer')
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLTableSectionElement>()
      render(
        <Table>
          <TableFooter ref={ref}>
            <tr>
              <td>Ref Footer</td>
            </tr>
          </TableFooter>
        </Table>
      )
      expect(ref.current).toBeInstanceOf(HTMLTableSectionElement)
    })

    it('should forward HTML attributes', () => {
      render(
        <Table>
          <TableFooter data-testid="test-footer" id="footer-1">
            <tr>
              <td>Test Footer</td>
            </tr>
          </TableFooter>
        </Table>
      )
      const footer = screen.getByTestId('test-footer')
      expect(footer).toHaveAttribute('id', 'footer-1')
    })
  })

  describe('TableRow Component', () => {
    it('should render table row with default props', () => {
      render(
        <Table>
          <TableBody>
            <TableRow>
              <td>Row Content</td>
            </TableRow>
          </TableBody>
        </Table>
      )
      const row = screen.getByRole('row')
      expect(row).toBeInTheDocument()
      expect(row).toHaveClass(
        'border-b',
        'transition-colors',
        'hover:bg-muted/50',
        'data-[state=selected]:bg-muted'
      )
    })

    it('should render table row with custom className', () => {
      render(
        <Table>
          <TableBody>
            <TableRow className="custom-row">
              <td>Custom Row</td>
            </TableRow>
          </TableBody>
        </Table>
      )
      const row = screen.getByRole('row')
      expect(row).toHaveClass('custom-row')
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLTableRowElement>()
      render(
        <Table>
          <TableBody>
            <TableRow ref={ref}>
              <td>Ref Row</td>
            </TableRow>
          </TableBody>
        </Table>
      )
      expect(ref.current).toBeInstanceOf(HTMLTableRowElement)
    })

    it('should forward HTML attributes', () => {
      render(
        <Table>
          <TableBody>
            <TableRow data-testid="test-row" id="row-1">
              <td>Test Row</td>
            </TableRow>
          </TableBody>
        </Table>
      )
      const row = screen.getByTestId('test-row')
      expect(row).toHaveAttribute('id', 'row-1')
    })
  })

  describe('TableHead Component', () => {
    it('should render table head with default props', () => {
      render(
        <Table>
          <TableHeader>
            <tr>
              <TableHead>Header Cell</TableHead>
            </tr>
          </TableHeader>
        </Table>
      )
      const head = screen.getByRole('columnheader', { name: 'Header Cell' })
      expect(head).toBeInTheDocument()
      expect(head).toHaveClass(
        'h-12',
        'px-4',
        'text-left',
        'align-middle',
        'font-medium',
        'text-muted-foreground',
        '[&:has([role=checkbox])]:pr-0'
      )
    })

    it('should render table head with custom className', () => {
      render(
        <Table>
          <TableHeader>
            <tr>
              <TableHead className="custom-head">Custom Head</TableHead>
            </tr>
          </TableHeader>
        </Table>
      )
      const head = screen.getByRole('columnheader', { name: 'Custom Head' })
      expect(head).toHaveClass('custom-head')
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLTableCellElement>()
      render(
        <Table>
          <TableHeader>
            <tr>
              <TableHead ref={ref}>Ref Head</TableHead>
            </tr>
          </TableHeader>
        </Table>
      )
      expect(ref.current).toBeInstanceOf(HTMLTableCellElement)
    })

    it('should forward HTML attributes', () => {
      render(
        <Table>
          <TableHeader>
            <tr>
              <TableHead data-testid="test-head" id="head-1">Test Head</TableHead>
            </tr>
          </TableHeader>
        </Table>
      )
      const head = screen.getByTestId('test-head')
      expect(head).toHaveAttribute('id', 'head-1')
    })

    it('should render as th element', () => {
      render(
        <Table>
          <TableHeader>
            <tr>
              <TableHead>Th Element</TableHead>
            </tr>
          </TableHeader>
        </Table>
      )
      const head = screen.getByRole('columnheader', { name: 'Th Element' })
      expect(head.tagName).toBe('TH')
    })
  })

  describe('TableCell Component', () => {
    it('should render table cell with default props', () => {
      render(
        <Table>
          <TableBody>
            <tr>
              <TableCell>Cell Content</TableCell>
            </tr>
          </TableBody>
        </Table>
      )
      const cell = screen.getByRole('cell', { name: 'Cell Content' })
      expect(cell).toBeInTheDocument()
      expect(cell).toHaveClass('p-4', 'align-middle', '[&:has([role=checkbox])]:pr-0')
    })

    it('should render table cell with custom className', () => {
      render(
        <Table>
          <TableBody>
            <tr>
              <TableCell className="custom-cell">Custom Cell</TableCell>
            </tr>
          </TableBody>
        </Table>
      )
      const cell = screen.getByRole('cell', { name: 'Custom Cell' })
      expect(cell).toHaveClass('custom-cell')
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLTableCellElement>()
      render(
        <Table>
          <TableBody>
            <tr>
              <TableCell ref={ref}>Ref Cell</TableCell>
            </tr>
          </TableBody>
        </Table>
      )
      expect(ref.current).toBeInstanceOf(HTMLTableCellElement)
    })

    it('should forward HTML attributes', () => {
      render(
        <Table>
          <TableBody>
            <tr>
              <TableCell data-testid="test-cell" id="cell-1">Test Cell</TableCell>
            </tr>
          </TableBody>
        </Table>
      )
      const cell = screen.getByTestId('test-cell')
      expect(cell).toHaveAttribute('id', 'cell-1')
    })

    it('should render as td element', () => {
      render(
        <Table>
          <TableBody>
            <tr>
              <TableCell>Td Element</TableCell>
            </tr>
          </TableBody>
        </Table>
      )
      const cell = screen.getByRole('cell', { name: 'Td Element' })
      expect(cell.tagName).toBe('TD')
    })
  })

  describe('TableCaption Component', () => {
    it('should render table caption with default props', () => {
      render(
        <Table>
          <TableCaption>Table Caption</TableCaption>
          <TableBody>
            <tr>
              <td>Content</td>
            </tr>
          </TableBody>
        </Table>
      )
      const caption = screen.getByText('Table Caption')
      expect(caption).toBeInTheDocument()
      expect(caption).toHaveClass('mt-4', 'text-sm', 'text-muted-foreground')
    })

    it('should render table caption with custom className', () => {
      render(
        <Table>
          <TableCaption className="custom-caption">Custom Caption</TableCaption>
          <TableBody>
            <tr>
              <td>Content</td>
            </tr>
          </TableBody>
        </Table>
      )
      const caption = screen.getByText('Custom Caption')
      expect(caption).toHaveClass('custom-caption')
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLTableCaptionElement>()
      render(
        <Table>
          <TableCaption ref={ref}>Ref Caption</TableCaption>
          <TableBody>
            <tr>
              <td>Content</td>
            </tr>
          </TableBody>
        </Table>
      )
      expect(ref.current).toBeInstanceOf(HTMLTableCaptionElement)
    })

    it('should forward HTML attributes', () => {
      render(
        <Table>
          <TableCaption data-testid="test-caption" id="caption-1">Test Caption</TableCaption>
          <TableBody>
            <tr>
              <td>Content</td>
            </tr>
          </TableBody>
        </Table>
      )
      const caption = screen.getByTestId('test-caption')
      expect(caption).toHaveAttribute('id', 'caption-1')
    })

    it('should render as caption element', () => {
      render(
        <Table>
          <TableCaption>Caption Element</TableCaption>
          <TableBody>
            <tr>
              <td>Content</td>
            </tr>
          </TableBody>
        </Table>
      )
      const caption = screen.getByText('Caption Element')
      expect(caption.tagName).toBe('CAPTION')
    })
  })

  describe('Table Composition', () => {
    it('should render complete table structure', () => {
      render(
        <Table>
          <TableCaption>Complete Table Example</TableCaption>
          <TableHeader>
            <tr>
              <TableHead>Name</TableHead>
              <TableHead>Age</TableHead>
            </tr>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell>John</TableCell>
              <TableCell>25</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>Jane</TableCell>
              <TableCell>30</TableCell>
            </TableRow>
          </TableBody>
          <TableFooter>
            <tr>
              <TableCell>Total: 2</TableCell>
            </tr>
          </TableFooter>
        </Table>
      )

      expect(screen.getByText('Complete Table Example')).toBeInTheDocument()
      expect(screen.getByRole('columnheader', { name: 'Name' })).toBeInTheDocument()
      expect(screen.getByRole('columnheader', { name: 'Age' })).toBeInTheDocument()
      expect(screen.getByRole('cell', { name: 'John' })).toBeInTheDocument()
      expect(screen.getByRole('cell', { name: '25' })).toBeInTheDocument()
      expect(screen.getByRole('cell', { name: 'Jane' })).toBeInTheDocument()
      expect(screen.getByRole('cell', { name: '30' })).toBeInTheDocument()
      expect(screen.getByRole('cell', { name: 'Total: 2' })).toBeInTheDocument()
    })

    it('should handle nested table structures', () => {
      render(
        <Table>
          <TableBody>
            <TableRow>
              <TableCell>
                <Table>
                  <TableBody>
                    <TableRow>
                      <TableCell>Nested Content</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      )

      expect(screen.getAllByText('Nested Content')[0]).toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty children', () => {
      render(<Table></Table>)
      const table = screen.getByRole('table')
      expect(table).toBeInTheDocument()
    })

    it('should handle null children', () => {
      render(<Table>{null}</Table>)
      const table = screen.getByRole('table')
      expect(table).toBeInTheDocument()
    })

    it('should handle undefined children', () => {
      render(<Table>{undefined}</Table>)
      const table = screen.getByRole('table')
      expect(table).toBeInTheDocument()
    })

    it('should handle multiple className values', () => {
      render(
        <Table className="class1 class2">
          <TableBody>
            <TableRow>
              <TableCell>Multi Class Table</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      )
      const table = screen.getByRole('table')
      expect(table).toHaveClass('class1', 'class2')
    })

    it('should handle very long content', () => {
      const longContent = 'A'.repeat(1000)
      render(
        <Table>
          <TableBody>
            <TableRow>
              <TableCell>{longContent}</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      )
      const cell = screen.getByRole('cell', { name: longContent })
      expect(cell).toBeInTheDocument()
    })

    it('should handle special characters in content', () => {
      const specialContent = '!@#$%^&*()_+-=[]{}|;:,.<>?'
      render(
        <Table>
          <TableBody>
            <TableRow>
              <TableCell>{specialContent}</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      )
      const cell = screen.getByRole('cell', { name: specialContent })
      expect(cell).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('should have correct semantic structure', () => {
      render(
        <Table>
          <TableCaption>Accessible Table</TableCaption>
          <TableHeader>
            <tr>
              <TableHead>Column 1</TableHead>
            </tr>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell>Data 1</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      )

      const table = screen.getByRole('table')
      const caption = screen.getByText('Accessible Table')
      const header = screen.getAllByRole('rowgroup')[0]
      const body = screen.getAllByRole('rowgroup')[1]

      expect(table).toContainElement(caption)
      expect(table).toContainElement(header)
      expect(table).toContainElement(body)
    })

    it('should support aria attributes', () => {
      render(
        <Table aria-label="Custom table label">
          <TableBody>
            <TableRow>
              <TableCell>Content</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      )
      const table = screen.getByRole('table', { name: 'Custom table label' })
      expect(table).toBeInTheDocument()
    })
  })
})
