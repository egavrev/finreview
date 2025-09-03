import React from 'react'
import { render, screen, fireEvent } from '../../../lib/test-utils'
import { Input } from '../input'

describe('Input Component', () => {
  describe('Rendering', () => {
    it('should render input with default props', () => {
      render(<Input placeholder="Enter text" />)
      const input = screen.getByPlaceholderText('Enter text')
      expect(input).toBeInTheDocument()
      // HTML inputs don't have a default type attribute when not specified
      expect(input).not.toHaveAttribute('type')
    })

    it('should render input with custom className', () => {
      render(<Input className="custom-input" placeholder="Custom Input" />)
      const input = screen.getByPlaceholderText('Custom Input')
      expect(input).toHaveClass('custom-input')
    })

    it('should forward ref correctly', () => {
      const ref = React.createRef<HTMLInputElement>()
      render(<Input ref={ref} placeholder="Ref Input" />)
      expect(ref.current).toBeInstanceOf(HTMLInputElement)
    })
  })

  describe('Input Types', () => {
    it('should render text input by default', () => {
      render(<Input placeholder="Text Input" />)
      const input = screen.getByPlaceholderText('Text Input')
      // HTML inputs don't have a default type attribute when not specified
      expect(input).not.toHaveAttribute('type')
    })

    it('should render email input correctly', () => {
      render(<Input type="email" placeholder="Email Input" />)
      const input = screen.getByPlaceholderText('Email Input')
      expect(input).toHaveAttribute('type', 'email')
    })

    it('should render password input correctly', () => {
      render(<Input type="password" placeholder="Password Input" />)
      const input = screen.getByPlaceholderText('Password Input')
      expect(input).toHaveAttribute('type', 'password')
    })

    it('should render number input correctly', () => {
      render(<Input type="number" placeholder="Number Input" />)
      const input = screen.getByPlaceholderText('Number Input')
      expect(input).toHaveAttribute('type', 'number')
    })

    it('should render date input correctly', () => {
      render(<Input type="date" placeholder="Date Input" />)
      const input = screen.getByPlaceholderText('Date Input')
      expect(input).toHaveAttribute('type', 'date')
    })

    it('should render file input correctly', () => {
      render(<Input type="file" />)
      const input = screen.getByDisplayValue('')
      expect(input).toHaveAttribute('type', 'file')
    })

    it('should render search input correctly', () => {
      render(<Input type="search" placeholder="Search Input" />)
      const input = screen.getByPlaceholderText('Search Input')
      expect(input).toHaveAttribute('type', 'search')
    })

    it('should render tel input correctly', () => {
      render(<Input type="tel" placeholder="Phone Input" />)
      const input = screen.getByPlaceholderText('Phone Input')
      expect(input).toHaveAttribute('type', 'tel')
    })

    it('should render url input correctly', () => {
      render(<Input type="url" placeholder="URL Input" />)
      const input = screen.getByPlaceholderText('URL Input')
      expect(input).toHaveAttribute('type', 'url')
    })
  })

  describe('Interactive States', () => {
    it('should handle value changes', () => {
      render(<Input placeholder="Changeable Input" />)
      const input = screen.getByPlaceholderText('Changeable Input')
      
      fireEvent.change(input, { target: { value: 'New Value' } })
      expect(input).toHaveValue('New Value')
    })

    it('should handle focus events', () => {
      const handleFocus = jest.fn()
      render(<Input onFocus={handleFocus} placeholder="Focusable Input" />)
      const input = screen.getByPlaceholderText('Focusable Input')
      
      fireEvent.focus(input)
      expect(handleFocus).toHaveBeenCalledTimes(1)
    })

    it('should handle blur events', () => {
      const handleBlur = jest.fn()
      render(<Input onBlur={handleBlur} placeholder="Blur Input" />)
      const input = screen.getByPlaceholderText('Blur Input')
      
      fireEvent.blur(input)
      expect(handleBlur).toHaveBeenCalledTimes(1)
    })

    it('should handle key events', () => {
      const handleKeyDown = jest.fn()
      const handleKeyUp = jest.fn()
      render(
        <Input
          onKeyDown={handleKeyDown}
          onKeyUp={handleKeyUp}
          placeholder="Key Input"
        />
      )
      const input = screen.getByPlaceholderText('Key Input')
      
      fireEvent.keyDown(input, { key: 'Enter' })
      fireEvent.keyUp(input, { key: 'Enter' })
      
      expect(handleKeyDown).toHaveBeenCalledTimes(1)
      expect(handleKeyUp).toHaveBeenCalledTimes(1)
    })

    it('should handle disabled state', () => {
      render(<Input disabled placeholder="Disabled Input" />)
      const input = screen.getByPlaceholderText('Disabled Input')
      
      expect(input).toBeDisabled()
      expect(input).toHaveClass('disabled:cursor-not-allowed', 'disabled:opacity-50')
    })

    it('should handle readonly state', () => {
      render(<Input readOnly placeholder="Readonly Input" />)
      const input = screen.getByPlaceholderText('Readonly Input')
      
      expect(input).toHaveAttribute('readonly')
    })
  })

  describe('Styling and Classes', () => {
    it('should have correct base classes', () => {
      render(<Input placeholder="Styled Input" />)
      const input = screen.getByPlaceholderText('Styled Input')
      
      expect(input).toHaveClass(
        'flex',
        'h-10',
        'w-full',
        'rounded-md',
        'border',
        'border-input',
        'bg-background',
        'px-3',
        'py-2',
        'text-sm'
      )
    })

    it('should have correct focus classes', () => {
      render(<Input placeholder="Focus Input" />)
      const input = screen.getByPlaceholderText('Focus Input')
      
      expect(input).toHaveClass(
        'focus-visible:outline-none',
        'focus-visible:ring-2',
        'focus-visible:ring-ring',
        'focus-visible:ring-offset-2'
      )
    })

    it('should have correct placeholder styling', () => {
      render(<Input placeholder="Placeholder Input" />)
      const input = screen.getByPlaceholderText('Placeholder Input')
      
      expect(input).toHaveClass('placeholder:text-muted-foreground')
    })

    it('should have correct file input styling', () => {
      render(<Input type="file" />)
      const input = screen.getByDisplayValue('')
      
      expect(input).toHaveClass(
        'file:border-0',
        'file:bg-transparent',
        'file:text-sm',
        'file:font-medium'
      )
    })
  })

  describe('Accessibility', () => {
    it('should support aria-label', () => {
      render(<Input aria-label="Custom label" />)
      const input = screen.getByRole('textbox', { name: 'Custom label' })
      expect(input).toBeInTheDocument()
    })

    it('should support aria-describedby', () => {
      render(
        <div>
          <Input aria-describedby="description" />
          <div id="description">Input description</div>
        </div>
      )
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('aria-describedby', 'description')
    })

    it('should support aria-invalid', () => {
      render(<Input aria-invalid="true" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('aria-invalid', 'true')
    })

    it('should support aria-required', () => {
      render(<Input aria-required="true" />)
      const input = screen.getByRole('textbox')
      expect(input).toHaveAttribute('aria-required', 'true')
    })
  })

  describe('Props Forwarding', () => {
    it('should forward HTML input attributes', () => {
      render(
        <Input
          name="test-input"
          id="test-id"
          placeholder="Test Input"
          maxLength={50}
          minLength={5}
          pattern="[A-Za-z]+"
          required
          autoComplete="off"
        />
      )
      const input = screen.getByPlaceholderText('Test Input')
      
      expect(input).toHaveAttribute('name', 'test-input')
      expect(input).toHaveAttribute('id', 'test-id')
      expect(input).toHaveAttribute('maxLength', '50')
      expect(input).toHaveAttribute('minLength', '5')
      expect(input).toHaveAttribute('pattern', '[A-Za-z]+')
      expect(input).toHaveAttribute('required')
      expect(input).toHaveAttribute('autoComplete', 'off')
    })

    it('should handle data attributes', () => {
      render(<Input data-testid="custom-input" placeholder="Data Input" />)
      const input = screen.getByTestId('custom-input')
      expect(input).toBeInTheDocument()
    })

    it('should handle custom event handlers', () => {
      const handleInput = jest.fn()
      const handlePaste = jest.fn()
      const handleCut = jest.fn()
      
      render(
        <Input
          onInput={handleInput}
          onPaste={handlePaste}
          onCut={handleCut}
          placeholder="Event Input"
        />
      )
      const input = screen.getByPlaceholderText('Event Input')
      
      fireEvent.input(input, { target: { value: 'test' } })
      fireEvent.paste(input)
      fireEvent.cut(input)
      
      expect(handleInput).toHaveBeenCalledTimes(1)
      expect(handlePaste).toHaveBeenCalledTimes(1)
      expect(handleCut).toHaveBeenCalledTimes(1)
    })
  })

  describe('Edge Cases', () => {
    it('should handle empty placeholder', () => {
      render(<Input placeholder="" />)
      const input = screen.getByRole('textbox')
      expect(input).toBeInTheDocument()
    })

    it('should handle null placeholder', () => {
      render(<Input placeholder={null as any} />)
      const input = screen.getByRole('textbox')
      expect(input).toBeInTheDocument()
    })

    it('should handle undefined placeholder', () => {
      render(<Input placeholder={undefined} />)
      const input = screen.getByRole('textbox')
      expect(input).toBeInTheDocument()
    })

    it('should handle very long placeholder text', () => {
      const longPlaceholder = 'A'.repeat(1000)
      render(<Input placeholder={longPlaceholder} />)
      const input = screen.getByPlaceholderText(longPlaceholder)
      expect(input).toBeInTheDocument()
    })

    it('should handle special characters in placeholder', () => {
      const specialPlaceholder = '!@#$%^&*()_+-=[]{}|;:,.<>?'
      render(<Input placeholder={specialPlaceholder} />)
      const input = screen.getByPlaceholderText(specialPlaceholder)
      expect(input).toBeInTheDocument()
    })
  })
})
