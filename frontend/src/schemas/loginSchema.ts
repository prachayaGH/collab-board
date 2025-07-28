import { z } from 'zod'

export const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address'),
  password: z
    .string()
    .min(1, 'Password is required')
    .min(8, 'Password must be at least 8 characters')
})

export type LoginData = z.infer<typeof loginSchema>

export interface ValidationErrors {
  email?: string
  password?: string
}

export class LoginValidator {
  static validateField(field: keyof LoginData, value: string): string | null {
    try {
      if (field === 'email') {
        loginSchema.shape.email.parse(value)
      } else if (field === 'password') {
        loginSchema.shape.password.parse(value)
      }
      return null
    } catch (error) {
      if (error instanceof z.ZodError) {
        return error.issues[0].message
      }
      return null
    }
  }

  static validateForm(data: LoginData): { isValid: boolean; errors: ValidationErrors } {
    try {
      loginSchema.parse(data)
      return { isValid: true, errors: {} }
    } catch (error) {
      const errors: ValidationErrors = {}

      if (error instanceof z.ZodError) {
        error.issues.forEach((err) => {
          const field = err.path[0] as keyof ValidationErrors
          errors[field] = err.message
        })
      }

      return { isValid: false, errors }
    }
  }
}
