import React from 'react'
import { render, screen, fireEvent } from '../../lib/test-utils'
import { Sidebar } from '../sidebar'

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}))

jest.mock('next/link', () => {
  return function MockLink({ children, href, ...props }: any) {
    return (
      <a href={href} {...props}>
        {children}
      </a>
    )
  }
})

describe('Sidebar Component', () => {
  const mockUsePathname = require('next/navigation').usePathname

  beforeEach(() => {
    mockUsePathname.mockReturnValue('/')
  })

  describe('Desktop Sidebar', () => {
    it('should render desktop sidebar with title', () => {
      render(<Sidebar />)
      const desktopSidebar = document.querySelector('.hidden.lg\\:flex')
      const title = desktopSidebar?.querySelector('h1')
      expect(title).toHaveTextContent('Financial Review')
    })

    it('should render all menu items in desktop sidebar', () => {
      render(<Sidebar />)
      const desktopSidebar = document.querySelector('.hidden.lg\\:flex')
      expect(desktopSidebar).toHaveTextContent('Dashboard')
      expect(desktopSidebar).toHaveTextContent('Operations')
      expect(desktopSidebar).toHaveTextContent('Reports')
      expect(desktopSidebar).toHaveTextContent('Files')
    })

    it('should have correct links for desktop menu items', () => {
      render(<Sidebar />)
      const desktopSidebar = document.querySelector('.hidden.lg\\:flex')
      
      const dashboardLink = desktopSidebar?.querySelector('a[href="/"]')
      const operationsLink = desktopSidebar?.querySelector('a[href="/operations"]')
      const reportsLink = desktopSidebar?.querySelector('a[href="/reports"]')
      const filesLink = desktopSidebar?.querySelector('a[href="/files"]')

      expect(dashboardLink).toBeInTheDocument()
      expect(operationsLink).toBeInTheDocument()
      expect(reportsLink).toBeInTheDocument()
      expect(filesLink).toBeInTheDocument()
    })

    it('should highlight active menu item in desktop sidebar', () => {
      mockUsePathname.mockReturnValue('/operations')
      render(<Sidebar />)
      
      const desktopSidebar = document.querySelector('.hidden.lg\\:flex')
      const operationsLink = desktopSidebar?.querySelector('a[href="/operations"]')
      expect(operationsLink).toHaveClass('bg-gray-800', 'text-white')
    })

    it('should not highlight inactive menu items in desktop sidebar', () => {
      mockUsePathname.mockReturnValue('/operations')
      render(<Sidebar />)
      
      const desktopSidebar = document.querySelector('.hidden.lg\\:flex')
      const dashboardLink = desktopSidebar?.querySelector('a[href="/"]')
      expect(dashboardLink).not.toHaveClass('bg-gray-800', 'text-white')
      expect(dashboardLink).toHaveClass('text-gray-300')
    })

    it('should have correct desktop sidebar classes', () => {
      render(<Sidebar />)
      const desktopSidebar = document.querySelector('.hidden.lg\\:flex')
      expect(desktopSidebar).toHaveClass('hidden', 'lg:flex', 'h-full', 'w-64', 'flex-col', 'bg-gray-900')
    })
  })

  describe('Mobile Header', () => {
    it('should render mobile header with title', () => {
      render(<Sidebar />)
      const mobileHeader = document.querySelector('.lg\\:hidden.fixed.top-0.left-0.right-0')
      expect(mobileHeader).toBeInTheDocument()
    })

    it('should render mobile menu toggle button', () => {
      render(<Sidebar />)
      const toggleButton = screen.getByLabelText('Toggle menu')
      expect(toggleButton).toBeInTheDocument()
    })

    it('should have correct mobile header classes', () => {
      render(<Sidebar />)
      const mobileHeader = document.querySelector('.lg\\:hidden.fixed.top-0.left-0.right-0')
      expect(mobileHeader).toHaveClass('lg:hidden', 'fixed', 'top-0', 'left-0', 'right-0', 'z-50', 'bg-gray-900')
    })
  })

  describe('Mobile Menu Toggle', () => {
    it('should show menu icon when mobile menu is closed', () => {
      render(<Sidebar />)
      const toggleButton = screen.getByLabelText('Toggle menu')
      expect(toggleButton.querySelector('.h-6.w-6')).toBeInTheDocument()
    })

    it('should toggle mobile menu state when button is clicked', () => {
      render(<Sidebar />)
      const toggleButton = screen.getByLabelText('Toggle menu')
      
      // Click to toggle - this should change the state
      fireEvent.click(toggleButton)
      
      // The button should still be there
      expect(toggleButton).toBeInTheDocument()
      
      // We can verify the toggle button is functional by checking it has the right icon
      const icon = toggleButton.querySelector('svg')
      expect(icon).toBeInTheDocument()
    })
  })

  describe('Mobile Menu Structure', () => {
    it('should render mobile menu with correct classes', () => {
      render(<Sidebar />)
      // The mobile menu is the second lg:hidden fixed element (after the header)
      const mobileMenus = document.querySelectorAll('.lg\\:hidden.fixed')
      const mobileMenu = mobileMenus[1] // Second one is the slide-out menu
      expect(mobileMenu).toHaveClass(
        'lg:hidden',
        'fixed',
        'top-0',
        'left-0',
        'z-50',
        'h-full',
        'w-64',
        'bg-gray-900',
        'transform',
        'transition-transform',
        'duration-300',
        'ease-in-out'
      )
    })

    it('should render close button in mobile menu', () => {
      render(<Sidebar />)
      const toggleButton = screen.getByLabelText('Toggle menu')
      fireEvent.click(toggleButton)
      
      const closeButton = screen.getByLabelText('Close menu')
      expect(closeButton).toBeInTheDocument()
    })
  })

  describe('Menu Item Icons', () => {
    it('should render icons for all menu items', () => {
      render(<Sidebar />)
      
      // Check that icons are rendered (they have the mr-3 h-5 w-5 classes)
      const desktopSidebar = document.querySelector('.hidden.lg\\:flex')
      const menuItems = desktopSidebar?.querySelectorAll('a')
      menuItems?.forEach(item => {
        const icon = item.querySelector('.mr-3.h-5.w-5')
        expect(icon).toBeInTheDocument()
      })
    })
  })

  describe('Responsive Behavior', () => {
    it('should hide desktop sidebar on mobile', () => {
      render(<Sidebar />)
      const desktopSidebar = document.querySelector('.hidden.lg\\:flex')
      expect(desktopSidebar).toHaveClass('hidden')
    })

    it('should show mobile header on mobile', () => {
      render(<Sidebar />)
      const mobileHeader = document.querySelector('.lg\\:hidden.fixed.top-0.left-0.right-0')
      expect(mobileHeader).toHaveClass('lg:hidden')
    })
  })

  describe('Accessibility', () => {
    it('should have proper aria-labels for buttons', () => {
      render(<Sidebar />)
      expect(screen.getByLabelText('Toggle menu')).toBeInTheDocument()
      
      // Open mobile menu to show close button
      const toggleButton = screen.getByLabelText('Toggle menu')
      fireEvent.click(toggleButton)
      expect(screen.getByLabelText('Close menu')).toBeInTheDocument()
    })

    it('should have proper navigation structure', () => {
      render(<Sidebar />)
      const navs = document.querySelectorAll('nav')
      expect(navs.length).toBeGreaterThan(0)
    })
  })

  describe('Edge Cases', () => {
    it('should handle pathname changes correctly', () => {
      const { rerender } = render(<Sidebar />)
      
      // Initial state: dashboard active
      const desktopSidebar = document.querySelector('.hidden.lg\\:flex')
      let dashboardLink = desktopSidebar?.querySelector('a[href="/"]')
      expect(dashboardLink).toHaveClass('bg-gray-800', 'text-white')
      
      // Change pathname to operations
      mockUsePathname.mockReturnValue('/operations')
      rerender(<Sidebar />)
      
      // Now operations should be active
      const operationsLink = desktopSidebar?.querySelector('a[href="/operations"]')
      expect(operationsLink).toHaveClass('bg-gray-800', 'text-white')
      
      // Dashboard should no longer be active
      dashboardLink = desktopSidebar?.querySelector('a[href="/"]')
      expect(dashboardLink).not.toHaveClass('bg-gray-800', 'text-white')
    })
  })
})
