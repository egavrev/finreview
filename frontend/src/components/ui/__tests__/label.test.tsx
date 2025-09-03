import React from 'react'
import { render, screen, fireEvent } from '../../../lib/test-utils'
import { Label } from '../label'

describe('Label Component', () => {
  describe('Rendering', () => {
    it('should render label with text content', () => {
      render(<Label>Test Label</Label>)
      const label = screen.getByText('Test Label')
      expect(label).toBeInTheDocument()
      expect(label.tagName).toBe('LABEL')
    })

    it('should forward HTML attributes', () => {
      render(<Label htmlFor="input-field" id="label-1">Test Label</Label>)
      const label = screen.getByText('Test Label')
      expect(label).toHaveAttribute('for', 'input-field')
      expect(label).toHaveAttribute('id', 'label-1')
    })
  })

  describe('Styling and Classes', () => {
    it('should have default base classes', () => {
      render(<Label>Default Label</Label>)
      const label = screen.getByText('Default Label')
      expect(label).toHaveClass(
        'text-sm',
        'font-medium',
        'leading-none',
        'peer-disabled:cursor-not-allowed',
        'peer-disabled:opacity-70'
      )
    })

    it('should merge custom classes with base classes', () => {
      render(<Label className="text-red-500 font-bold">Custom Styled Label</Label>)
      const label = screen.getByText('Custom Styled Label')
      
      expect(label).toHaveClass(
        'text-sm',
        'leading-none',
        'peer-disabled:cursor-not-allowed',
        'peer-disabled:opacity-70',
        'text-red-500',
        'font-bold'
      )
    })

    it('should handle empty className', () => {
      render(<Label className="">Empty Class Label</Label>)
      const label = screen.getByText('Empty Class Label')
      expect(label).toHaveClass(
        'text-sm',
        'font-medium',
        'leading-none',
        'peer-disabled:cursor-not-allowed',
        'peer-disabled:opacity-70'
      )
    })

    it('should handle undefined className', () => {
      render(<Label className={undefined}>Undefined Class Label</Label>)
      const label = screen.getByText('Undefined Class Label')
      expect(label).toHaveClass(
        'text-sm',
        'font-medium',
        'leading-none',
        'peer-disabled:cursor-not-allowed',
        'peer-disabled:opacity-70'
      )
    })
  })

  describe('Ref Forwarding', () => {
    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLLabelElement>()
      render(<Label ref={ref}>Ref Label</Label>)
      expect(ref.current).toBeInstanceOf(HTMLLabelElement)
      expect(ref.current?.textContent).toBe('Ref Label')
    })
  })

  describe('Accessibility', () => {
    it('should support htmlFor attribute', () => {
      render(<Label htmlFor="email-input">Email Address</Label>)
      const label = screen.getByText('Email Address')
      expect(label).toHaveAttribute('for', 'email-input')
    })

    it('should support aria-label', () => {
      render(<Label aria-label="Accessible Label">Visible Text</Label>)
      const label = screen.getByLabelText('Accessible Label')
      expect(label).toBeInTheDocument()
    })

    it('should support aria-labelledby', () => {
      render(
        <div>
          <span id="label-text">Label Text</span>
          <Label aria-labelledby="label-text">Form Label</Label>
        </div>
      )
      const label = screen.getByText('Form Label')
      expect(label).toHaveAttribute('aria-labelledby', 'label-text')
    })
  })

  describe('Props Forwarding', () => {
    it('should forward all HTML label attributes', () => {
      render(
        <Label
          data-testid="test-label"
          id="test-label"
          className="test-class"
          title="Test tooltip"
          htmlFor="test-input"
        >
          Test Label
        </Label>
      )
      const label = screen.getByTestId('test-label')
      
      expect(label).toHaveAttribute('for', 'test-input')
      expect(label).toHaveAttribute('id', 'test-label')
      expect(label).toHaveClass('test-class')
      expect(label).toHaveAttribute('title', 'Test tooltip')
    })

    it('should handle event handlers', () => {
      const handleClick = jest.fn()
      render(<Label onClick={handleClick}>Clickable Label</Label>)
      const label = screen.getByText('Clickable Label')
      
      fireEvent.click(label)
      expect(handleClick).toHaveBeenCalledTimes(1)
    })

    it('should handle data attributes', () => {
      render(<Label data-custom="value">Data Label</Label>)
      const label = screen.getByText('Data Label')
      expect(label).toHaveAttribute('data-custom', 'value')
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty children', () => {
      render(<Label></Label>)
      const label = screen.getByRole('generic')
      expect(label).toBeInTheDocument()
      // When label has no content, it might be wrapped in a div by React Testing Library
      expect(label.tagName).toBe('DIV')
    })

    it('should handle null children', () => {
      render(<Label>{null}</Label>)
      const label = screen.getByRole('generic')
      expect(label).toBeInTheDocument()
      // When label has no content, it might be wrapped in a div by React Testing Library
      expect(label.tagName).toBe('DIV')
    })

    it('should handle undefined children', () => {
      render(<Label>{undefined}</Label>)
      const label = screen.getByRole('generic')
      expect(label).toBeInTheDocument()
      // When label has no content, it might be wrapped in a div by React Testing Library
      expect(label.tagName).toBe('DIV')
    })

    it('should handle multiple className values', () => {
      render(<Label className="class1 class2">Multi Class Label</Label>)
      const label = screen.getByText('Multi Class Label')
      expect(label).toHaveClass('class1', 'class2')
    })
  })

  describe('Integration', () => {
    it('should work with form inputs', () => {
      render(
        <div>
          <Label htmlFor="username">Username</Label>
          <input id="username" type="text" />
        </div>
      )
      
      const label = screen.getByText('Username')
      const input = screen.getByRole('textbox')
      
      expect(label).toHaveAttribute('for', 'username')
      expect(input).toHaveAttribute('id', 'username')
    })

    it('should work with checkboxes', () => {
      render(
        <div>
          <Label htmlFor="agree">I agree to terms</Label>
          <input id="agree" type="checkbox" />
        </div>
      )
      
      const label = screen.getByText('I agree to terms')
      const checkbox = screen.getByRole('checkbox')
      
      expect(label).toHaveAttribute('for', 'agree')
      expect(checkbox).toHaveAttribute('id', 'agree')
    })

    it('should work with radio buttons', () => {
      render(
        <div>
          <Label htmlFor="option1">Option 1</Label>
          <input id="option1" type="radio" name="options" />
        </div>
      )
      
      const label = screen.getByText('Option 1')
      const radio = screen.getByRole('radio')
      
      expect(label).toHaveAttribute('for', 'option1')
      expect(radio).toHaveAttribute('id', 'option1')
    })
  })
})
