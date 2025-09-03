import React from 'react'
import { render, screen } from '../../../lib/test-utils'
import { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent } from '../card'

describe('Card Components', () => {
  describe('Card Component', () => {
    it('should render card with default props', () => {
      render(<Card>Card Content</Card>)
      const card = screen.getByText('Card Content')
      expect(card).toBeInTheDocument()
      expect(card).toHaveClass('rounded-lg', 'border', 'bg-card', 'text-card-foreground', 'shadow-sm')
    })

    it('should render card with custom className', () => {
      render(<Card className="custom-card">Custom Card</Card>)
      const card = screen.getByText('Custom Card')
      expect(card).toHaveClass('custom-card')
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLDivElement>()
      render(<Card ref={ref}>Ref Card</Card>)
      expect(ref.current).toBeInstanceOf(HTMLDivElement)
    })

    it('should forward HTML attributes', () => {
      render(<Card data-testid="test-card" id="card-1">Test Card</Card>)
      const card = screen.getByTestId('test-card')
      expect(card).toHaveAttribute('id', 'card-1')
    })
  })

  describe('CardHeader Component', () => {
    it('should render card header with default props', () => {
      render(<CardHeader>Header Content</CardHeader>)
      const header = screen.getByText('Header Content')
      expect(header).toBeInTheDocument()
      expect(header).toHaveClass('flex', 'flex-col', 'space-y-1.5', 'p-6')
    })

    it('should render card header with custom className', () => {
      render(<CardHeader className="custom-header">Custom Header</CardHeader>)
      const header = screen.getByText('Custom Header')
      expect(header).toHaveClass('custom-header')
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLDivElement>()
      render(<CardHeader ref={ref}>Ref Header</CardHeader>)
      expect(ref.current).toBeInstanceOf(HTMLDivElement)
    })

    it('should forward HTML attributes', () => {
      render(<CardHeader data-testid="test-header" id="header-1">Test Header</CardHeader>)
      const header = screen.getByTestId('test-header')
      expect(header).toHaveAttribute('id', 'header-1')
    })
  })

  describe('CardTitle Component', () => {
    it('should render card title with default props', () => {
      render(<CardTitle>Card Title</CardTitle>)
      const title = screen.getByRole('heading', { level: 3, name: 'Card Title' })
      expect(title).toBeInTheDocument()
      expect(title).toHaveClass('text-2xl', 'font-semibold', 'leading-none', 'tracking-tight')
    })

    it('should render card title with custom className', () => {
      render(<CardTitle className="custom-title">Custom Title</CardTitle>)
      const title = screen.getByRole('heading', { level: 3, name: 'Custom Title' })
      expect(title).toHaveClass('custom-title')
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLHeadingElement>()
      render(<CardTitle ref={ref}>Ref Title</CardTitle>)
      expect(ref.current).toBeInstanceOf(HTMLHeadingElement)
    })

    it('should forward HTML attributes', () => {
      render(<CardTitle data-testid="test-title" id="title-1">Test Title</CardTitle>)
      const title = screen.getByTestId('test-title')
      expect(title).toHaveAttribute('id', 'title-1')
    })

    it('should render as h3 element', () => {
      render(<CardTitle>Heading Level</CardTitle>)
      const title = screen.getByRole('heading', { level: 3 })
      expect(title.tagName).toBe('H3')
    })
  })

  describe('CardDescription Component', () => {
    it('should render card description with default props', () => {
      render(<CardDescription>Card Description</CardDescription>)
      const description = screen.getByText('Card Description')
      expect(description).toBeInTheDocument()
      expect(description).toHaveClass('text-sm', 'text-muted-foreground')
    })

    it('should render card description with custom className', () => {
      render(<CardDescription className="custom-description">Custom Description</CardDescription>)
      const description = screen.getByText('Custom Description')
      expect(description).toHaveClass('custom-description')
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLParagraphElement>()
      render(<CardDescription ref={ref}>Ref Description</CardDescription>)
      expect(ref.current).toBeInstanceOf(HTMLParagraphElement)
    })

    it('should forward HTML attributes', () => {
      render(<CardDescription data-testid="test-description" id="desc-1">Test Description</CardDescription>)
      const description = screen.getByTestId('test-description')
      expect(description).toHaveAttribute('id', 'desc-1')
    })

    it('should render as p element', () => {
      render(<CardDescription>Paragraph Element</CardDescription>)
      const description = screen.getByText('Paragraph Element')
      expect(description.tagName).toBe('P')
    })
  })

  describe('CardContent Component', () => {
    it('should render card content with default props', () => {
      render(<CardContent>Content Text</CardContent>)
      const content = screen.getByText('Content Text')
      expect(content).toBeInTheDocument()
      expect(content).toHaveClass('p-6', 'pt-0')
    })

    it('should render card content with custom className', () => {
      render(<CardContent className="custom-content">Custom Content</CardContent>)
      const content = screen.getByText('Custom Content')
      expect(content).toHaveClass('custom-content')
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLDivElement>()
      render(<CardContent ref={ref}>Ref Content</CardContent>)
      expect(ref.current).toBeInstanceOf(HTMLDivElement)
    })

    it('should forward HTML attributes', () => {
      render(<CardContent data-testid="test-content" id="content-1">Test Content</CardContent>)
      const content = screen.getByTestId('test-content')
      expect(content).toHaveAttribute('id', 'content-1')
    })
  })

  describe('CardFooter Component', () => {
    it('should render card footer with default props', () => {
      render(<CardFooter>Footer Content</CardFooter>)
      const footer = screen.getByText('Footer Content')
      expect(footer).toBeInTheDocument()
      expect(footer).toHaveClass('flex', 'items-center', 'p-6', 'pt-0')
    })

    it('should render card footer with custom className', () => {
      render(<CardFooter className="custom-footer">Custom Footer</CardFooter>)
      const footer = screen.getByText('Custom Footer')
      expect(footer).toHaveClass('custom-footer')
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLDivElement>()
      render(<CardFooter ref={ref}>Ref Footer</CardFooter>)
      expect(ref.current).toBeInstanceOf(HTMLDivElement)
    })

    it('should forward HTML attributes', () => {
      render(<CardFooter data-testid="test-footer" id="footer-1">Test Footer</CardFooter>)
      const footer = screen.getByTestId('test-footer')
      expect(footer).toHaveAttribute('id', 'footer-1')
    })
  })

  describe('Card Composition', () => {
    it('should render complete card structure', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Complete Card</CardTitle>
            <CardDescription>This is a complete card example</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Main content goes here</p>
          </CardContent>
          <CardFooter>
            <button>Action Button</button>
          </CardFooter>
        </Card>
      )

      expect(screen.getByRole('heading', { name: 'Complete Card' })).toBeInTheDocument()
      expect(screen.getByText('This is a complete card example')).toBeInTheDocument()
      expect(screen.getByText('Main content goes here')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: 'Action Button' })).toBeInTheDocument()
    })

    it('should handle nested card structures', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Parent Card</CardTitle>
          </CardHeader>
          <CardContent>
            <Card>
              <CardHeader>
                <CardTitle>Child Card</CardTitle>
              </CardHeader>
              <CardContent>Nested content</CardContent>
            </Card>
          </CardContent>
        </Card>
      )

      expect(screen.getByRole('heading', { name: 'Parent Card' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: 'Child Card' })).toBeInTheDocument()
      expect(screen.getByText('Nested content')).toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty children', () => {
      render(<Card></Card>)
      const card = screen.getAllByText('')[0]
      expect(card).toBeInTheDocument()
      expect(card).toHaveTextContent('')
    })

    it('should handle null children', () => {
      render(<Card>{null}</Card>)
      const card = screen.getAllByText('')[0]
      expect(card).toBeInTheDocument()
    })

    it('should handle undefined children', () => {
      render(<Card>{undefined}</Card>)
      const card = screen.getAllByText('')[0]
      expect(card).toBeInTheDocument()
    })

    it('should handle multiple className values', () => {
      render(<Card className="class1 class2">Multi Class Card</Card>)
      const card = screen.getByText('Multi Class Card')
      expect(card).toHaveClass('class1', 'class2')
    })

    it('should handle very long content', () => {
      const longContent = 'A'.repeat(1000)
      render(<CardContent>{longContent}</CardContent>)
      const content = screen.getByText(longContent)
      expect(content).toBeInTheDocument()
    })

    it('should handle special characters in content', () => {
      const specialContent = '!@#$%^&*()_+-=[]{}|;:,.<>?'
      render(<CardTitle>{specialContent}</CardTitle>)
      const title = screen.getByRole('heading', { name: specialContent })
      expect(title).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('should have correct semantic structure', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Accessible Card</CardTitle>
            <CardDescription>Description for screen readers</CardDescription>
          </CardHeader>
          <CardContent>Main content</CardContent>
        </Card>
      )

      const card = screen.getByText('Accessible Card').closest('.rounded-lg')
      const title = screen.getByRole('heading', { name: 'Accessible Card' })
      const description = screen.getByText('Description for screen readers')
      const content = screen.getByText('Main content')

      expect(card).toContainElement(title)
      expect(card).toContainElement(description)
      expect(card).toContainElement(content)
    })

    it('should support aria attributes', () => {
      render(
        <Card aria-label="Custom card label">
          <CardContent>Content</CardContent>
        </Card>
      )
      const card = screen.getByRole('generic', { name: 'Custom card label' })
      expect(card).toBeInTheDocument()
    })
  })
})
