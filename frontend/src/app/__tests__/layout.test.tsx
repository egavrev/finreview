import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import RootLayout from '../layout'

// Mock the Sidebar component
jest.mock('@/components/sidebar', () => ({
  Sidebar: () => <div data-testid="sidebar">Sidebar Component</div>
}))

describe('RootLayout Component', () => {
  it('should render the root layout with metadata', () => {
    render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>
    )

    // Check that the layout renders
    expect(screen.getByTestId('sidebar')).toBeInTheDocument()
    expect(screen.getByText('Test Content')).toBeInTheDocument()
  })

  it('should render with correct HTML structure', () => {
    render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>
    )

    // Check that the main element is present
    const mainElement = screen.getByRole('main')
    expect(mainElement).toBeInTheDocument()
    expect(mainElement).toHaveClass('flex-1', 'overflow-auto', 'lg:ml-0', 'pt-16', 'lg:pt-0')
  })

  it('should render children content correctly', () => {
    const testContent = 'This is test content for the layout'
    
    render(
      <RootLayout>
        <div>{testContent}</div>
      </RootLayout>
    )

    expect(screen.getByText(testContent)).toBeInTheDocument()
  })

  it('should render with correct HTML structure and classes', () => {
    render(
      <RootLayout>
        <div>Test Content</div>
      </RootLayout>
    )

    // Check that the layout container has correct classes
    const container = screen.getByText('Test Content').closest('.flex.h-screen.bg-background')
    expect(container).toBeInTheDocument()
  })
})
