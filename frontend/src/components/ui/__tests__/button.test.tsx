import React from 'react'
import { render, screen, fireEvent } from '../../../lib/test-utils'
import { Button } from '../button'

describe('Button Component', () => {
  describe('Rendering', () => {
    it('should render button with default props', () => {
      render(<Button>Click me</Button>)
      const button = screen.getByRole('button', { name: 'Click me' })
      expect(button).toBeInTheDocument()
      expect(button).toHaveClass('bg-primary', 'text-primary-foreground')
    })

    it('should render button with custom className', () => {
      render(<Button className="custom-class">Custom Button</Button>)
      const button = screen.getByRole('button', { name: 'Custom Button' })
      expect(button).toHaveClass('custom-class')
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLButtonElement>()
      render(<Button ref={ref}>Ref Button</Button>)
      expect(ref.current).toBeInstanceOf(HTMLButtonElement)
    })
  })

  describe('Variants', () => {
    it('should render default variant correctly', () => {
      render(<Button variant="default">Default Button</Button>)
      const button = screen.getByRole('button', { name: 'Default Button' })
      expect(button).toHaveClass('bg-primary', 'text-primary-foreground')
    })

    it('should render destructive variant correctly', () => {
      render(<Button variant="destructive">Destructive Button</Button>)
      const button = screen.getByRole('button', { name: 'Destructive Button' })
      expect(button).toHaveClass('bg-destructive', 'text-destructive-foreground')
    })

    it('should render outline variant correctly', () => {
      render(<Button variant="outline">Outline Button</Button>)
      const button = screen.getByRole('button', { name: 'Outline Button' })
      expect(button).toHaveClass('border', 'border-input', 'bg-background')
    })

    it('should render secondary variant correctly', () => {
      render(<Button variant="secondary">Secondary Button</Button>)
      const button = screen.getByRole('button', { name: 'Secondary Button' })
      expect(button).toHaveClass('bg-secondary', 'text-secondary-foreground')
    })

    it('should render ghost variant correctly', () => {
      render(<Button variant="ghost">Ghost Button</Button>)
      const button = screen.getByRole('button', { name: 'Ghost Button' })
      expect(button).toHaveClass('hover:bg-accent', 'hover:text-accent-foreground')
    })

    it('should render link variant correctly', () => {
      render(<Button variant="link">Link Button</Button>)
      const button = screen.getByRole('button', { name: 'Link Button' })
      expect(button).toHaveClass('text-primary', 'underline-offset-4')
    })
  })

  describe('Sizes', () => {
    it('should render default size correctly', () => {
      render(<Button size="default">Default Size</Button>)
      const button = screen.getByRole('button', { name: 'Default Size' })
      expect(button).toHaveClass('h-10', 'px-4', 'py-2')
    })

    it('should render small size correctly', () => {
      render(<Button size="sm">Small Button</Button>)
      const button = screen.getByRole('button', { name: 'Small Button' })
      expect(button).toHaveClass('h-9', 'rounded-md', 'px-3')
    })

    it('should render large size correctly', () => {
      render(<Button size="lg">Large Button</Button>)
      const button = screen.getByRole('button', { name: 'Large Button' })
      expect(button).toHaveClass('h-11', 'rounded-md', 'px-8')
    })

    it('should render icon size correctly', () => {
      render(<Button size="icon">Icon Button</Button>)
      const button = screen.getByRole('button', { name: 'Icon Button' })
      expect(button).toHaveClass('h-10', 'w-10')
    })
  })

  describe('Interactive States', () => {
    it('should handle click events', () => {
      const handleClick = jest.fn()
      render(<Button onClick={handleClick}>Clickable Button</Button>)
      const button = screen.getByRole('button', { name: 'Clickable Button' })
      
      fireEvent.click(button)
      expect(handleClick).toHaveBeenCalledTimes(1)
    })

    it('should handle disabled state', () => {
      render(<Button disabled>Disabled Button</Button>)
      const button = screen.getByRole('button', { name: 'Disabled Button' })
      
      expect(button).toBeDisabled()
      expect(button).toHaveClass('disabled:pointer-events-none', 'disabled:opacity-50')
    })

    it('should handle focus states', () => {
      render(<Button>Focusable Button</Button>)
      const button = screen.getByRole('button', { name: 'Focusable Button' })
      
      expect(button).toHaveClass('focus-visible:outline-none', 'focus-visible:ring-2')
    })

    it('should handle hover states', () => {
      render(<Button variant="default">Hover Button</Button>)
      const button = screen.getByRole('button', { name: 'Hover Button' })
      
      expect(button).toHaveClass('hover:bg-primary/90')
    })
  })

  describe('Accessibility', () => {
    it('should have correct button role', () => {
      render(<Button>Accessible Button</Button>)
      const button = screen.getByRole('button', { name: 'Accessible Button' })
      expect(button).toBeInTheDocument()
    })

    it('should support aria-label', () => {
      render(<Button aria-label="Custom label">Button</Button>)
      const button = screen.getByRole('button', { name: 'Custom label' })
      expect(button).toBeInTheDocument()
    })

    it('should support aria-describedby', () => {
      render(
        <div>
          <Button aria-describedby="description">Button</Button>
          <div id="description">Button description</div>
        </div>
      )
      const button = screen.getByRole('button', { name: 'Button' })
      expect(button).toHaveAttribute('aria-describedby', 'description')
    })
  })

  describe('Props Forwarding', () => {
    it('should forward HTML button attributes', () => {
      render(
        <Button
          type="submit"
          form="test-form"
          name="test-button"
          value="test-value"
        >
          Submit Button
        </Button>
      )
      const button = screen.getByRole('button', { name: 'Submit Button' })
      
      expect(button).toHaveAttribute('type', 'submit')
      expect(button).toHaveAttribute('form', 'test-form')
      expect(button).toHaveAttribute('name', 'test-button')
      expect(button).toHaveAttribute('value', 'test-value')
    })

    it('should handle data attributes', () => {
      render(<Button data-testid="custom-button">Data Button</Button>)
      const button = screen.getByTestId('custom-button')
      expect(button).toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty children', () => {
      render(<Button></Button>)
      const button = screen.getByRole('button')
      expect(button).toBeInTheDocument()
      expect(button).toHaveTextContent('')
    })

    it('should handle null children', () => {
      render(<Button>{null}</Button>)
      const button = screen.getByRole('button')
      expect(button).toBeInTheDocument()
    })

    it('should handle undefined children', () => {
      render(<Button>{undefined}</Button>)
      const button = screen.getByRole('button')
      expect(button).toBeInTheDocument()
    })

    it('should handle multiple className values', () => {
      render(<Button className="class1 class2">Multi Class Button</Button>)
      const button = screen.getByRole('button', { name: 'Multi Class Button' })
      expect(button).toHaveClass('class1', 'class2')
    })
  })
})
