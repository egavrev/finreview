import { cn } from '../utils'

describe('cn utility function', () => {
  it('should merge class names correctly', () => {
    const result = cn('px-4 py-2', 'bg-blue-500', 'text-white')
    expect(result).toBe('px-4 py-2 bg-blue-500 text-white')
  })

  it('should handle conditional classes', () => {
    const isActive = true
    const isDisabled = false
    
    const result = cn(
      'base-class',
      isActive && 'active-class',
      isDisabled && 'disabled-class'
    )
    
    expect(result).toBe('base-class active-class')
  })

  it('should handle undefined and null values', () => {
    const result = cn('base-class', undefined, null, 'valid-class')
    expect(result).toBe('base-class valid-class')
  })

  it('should handle empty strings', () => {
    const result = cn('base-class', '', 'valid-class')
    expect(result).toBe('base-class valid-class')
  })

  it('should handle arrays of classes', () => {
    const result = cn(['px-4', 'py-2'], 'bg-blue-500')
    expect(result).toBe('px-4 py-2 bg-blue-500')
  })

  it('should handle objects with conditional classes', () => {
    const isActive = true
    const isDisabled = false
    
    const result = cn({
      'base-class': true,
      'active-class': isActive,
      'disabled-class': isDisabled,
      'hidden': false
    })
    
    expect(result).toBe('base-class active-class')
  })

  it('should handle mixed input types', () => {
    const isActive = true
    
    const result = cn(
      'base-class',
      ['px-4', 'py-2'],
      { 'active-class': isActive },
      'text-white'
    )
    
    expect(result).toBe('base-class px-4 py-2 active-class text-white')
  })

  it('should return empty string for no inputs', () => {
    const result = cn()
    expect(result).toBe('')
  })

  it('should handle single class input', () => {
    const result = cn('single-class')
    expect(result).toBe('single-class')
  })
})
