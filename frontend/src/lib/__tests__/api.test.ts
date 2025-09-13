import { API_BASE_URL, buildApiUrl, API_ENDPOINTS } from '../api'

// Mock environment variables
const originalEnv = process.env

describe('API Configuration', () => {
  beforeEach(() => {
    jest.resetModules()
    process.env = { ...originalEnv }
  })

  afterAll(() => {
    process.env = originalEnv
  })

  describe('API_BASE_URL', () => {
    it('should use environment variable when set', () => {
      process.env.NEXT_PUBLIC_API_BASE_URL = 'https://api.example.com'
      const { API_BASE_URL } = require('../api')
      expect(API_BASE_URL).toBe('https://api.example.com')
    })

    it('should fallback to localhost when environment variable is not set', () => {
      delete process.env.NEXT_PUBLIC_API_BASE_URL
      const { API_BASE_URL } = require('../api')
      expect(API_BASE_URL).toBe('http://localhost:8000')
    })

    it('should use localhost as default', () => {
      expect(API_BASE_URL).toBe('http://localhost:8000')
    })
  })

  describe('buildApiUrl', () => {
    it('should build URL correctly without leading slash', () => {
      const result = buildApiUrl('operations')
      expect(result).toBe('http://localhost:8000/operations')
    })

    it('should build URL correctly with leading slash', () => {
      const result = buildApiUrl('/operations')
      expect(result).toBe('http://localhost:8000/operations')
    })

    it('should handle empty endpoint', () => {
      const result = buildApiUrl('')
      expect(result).toBe('http://localhost:8000/')
    })

    it('should handle complex endpoints', () => {
      const result = buildApiUrl('operations/123/assign-type')
      expect(result).toBe('http://localhost:8000/operations/123/assign-type')
    })

    it('should handle endpoints with query parameters', () => {
      const result = buildApiUrl('operations?page=1&limit=10')
      expect(result).toBe('http://localhost:8000/operations?page=1&limit=10')
    })
  })

  describe('API_ENDPOINTS', () => {
    describe('PDF endpoints', () => {
      it('should have correct PDFS endpoint', () => {
        expect(API_ENDPOINTS.PDFS).toBe('http://localhost:8000/pdfs')
      })

      it('should build PDF_BY_ID endpoint correctly', () => {
        const result = API_ENDPOINTS.PDF_BY_ID(123)
        expect(result).toBe('http://localhost:8000/pdfs/123')
      })

      it('should build DELETE_PDF endpoint correctly', () => {
        const result = API_ENDPOINTS.DELETE_PDF(456)
        expect(result).toBe('http://localhost:8000/pdfs/456')
      })

      it('should have correct UPLOAD_PDF endpoint', () => {
        expect(API_ENDPOINTS.UPLOAD_PDF).toBe('http://localhost:8000/upload-pdf')
      })
    })

    describe('Operations endpoints', () => {
      it('should have correct OPERATIONS endpoint', () => {
        expect(API_ENDPOINTS.OPERATIONS).toBe('http://localhost:8000/operations')
      })

      it('should have correct OPERATIONS_NULL_TYPES endpoint', () => {
        expect(API_ENDPOINTS.OPERATIONS_NULL_TYPES).toBe('http://localhost:8000/operations/null-types')
      })

      it('should have correct OPERATIONS_WITH_TYPES endpoint', () => {
        expect(API_ENDPOINTS.OPERATIONS_WITH_TYPES).toBe('http://localhost:8000/operations/with-types')
      })

      it('should build OPERATIONS_BY_TYPE endpoint correctly', () => {
        const result = API_ENDPOINTS.OPERATIONS_BY_TYPE(789)
        expect(result).toBe('http://localhost:8000/operations/by-type/789')
      })

      it('should build OPERATIONS_BY_MONTH endpoint correctly', () => {
        const result = API_ENDPOINTS.OPERATIONS_BY_MONTH(2024, 1)
        expect(result).toBe('http://localhost:8000/operations/by-month/2024/1')
      })

      it('should build ASSIGN_OPERATION_TYPE endpoint correctly', () => {
        const result = API_ENDPOINTS.ASSIGN_OPERATION_TYPE(101)
        expect(result).toBe('http://localhost:8000/operations/101/assign-type')
      })

      it('should build DELETE_OPERATION endpoint correctly', () => {
        const result = API_ENDPOINTS.DELETE_OPERATION(202)
        expect(result).toBe('http://localhost:8000/operations/202')
      })

      it('should have correct CREATE_MANUAL_OPERATION endpoint', () => {
        expect(API_ENDPOINTS.CREATE_MANUAL_OPERATION).toBe('http://localhost:8000/operations/manual')
      })
    })

    describe('Operation types endpoints', () => {
      it('should have correct OPERATION_TYPES endpoint', () => {
        expect(API_ENDPOINTS.OPERATION_TYPES).toBe('http://localhost:8000/operation-types')
      })

      it('should build OPERATION_TYPE_BY_ID endpoint correctly', () => {
        const result = API_ENDPOINTS.OPERATION_TYPE_BY_ID(303)
        expect(result).toBe('http://localhost:8000/operation-types/303')
      })
    })

    describe('Reports endpoints', () => {
      it('should have correct AVAILABLE_MONTHS endpoint', () => {
        expect(API_ENDPOINTS.AVAILABLE_MONTHS).toBe('http://localhost:8000/reports/available-months')
      })

      it('should build MONTHLY_REPORT endpoint correctly', () => {
        const result = API_ENDPOINTS.MONTHLY_REPORT(2024, 3)
        expect(result).toBe('http://localhost:8000/reports/monthly/2024/3')
      })

      it('should build MONTHLY_OPERATIONS_BY_TYPE endpoint correctly', () => {
        const result = API_ENDPOINTS.MONTHLY_OPERATIONS_BY_TYPE(2024, 4, 404)
        expect(result).toBe('http://localhost:8000/reports/monthly/2024/4/type/404')
      })
    })

    describe('Statistics endpoints', () => {
      it('should have correct STATISTICS endpoint', () => {
        expect(API_ENDPOINTS.STATISTICS).toBe('http://localhost:8000/statistics')
      })
    })
  })

  describe('Edge cases', () => {
    it('should handle zero values in endpoints', () => {
      const result = API_ENDPOINTS.OPERATIONS_BY_MONTH(0, 0)
      expect(result).toBe('http://localhost:8000/operations/by-month/0/0')
    })

    it('should handle negative values in endpoints', () => {
      const result = API_ENDPOINTS.OPERATIONS_BY_MONTH(-1, -1)
      expect(result).toBe('http://localhost:8000/operations/by-month/-1/-1')
    })

    it('should handle very large numbers', () => {
      const result = API_ENDPOINTS.PDF_BY_ID(999999999)
      expect(result).toBe('http://localhost:8000/pdfs/999999999')
    })
  })
})
