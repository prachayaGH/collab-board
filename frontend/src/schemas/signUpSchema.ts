import { z } from 'zod'

// Zod Schema Definition
export const signUpSchema = z.object({
  firstName: z.string()
    .min(1, 'First name is required')
    .min(2, 'First name must be at least 2 characters')
    .max(50, 'First name must be less than 50 characters')
    .regex(/^[a-zA-Zก-๏\s]+$/, 'First name can only contain letters')
    .transform(val => val.trim()),

  lastName: z.string()
    .min(1, 'Last name is required')
    .min(2, 'Last name must be at least 2 characters')
    .max(50, 'Last name must be less than 50 characters')
    .regex(/^[a-zA-Zก-๏\s]+$/, 'Last name can only contain letters')
    .transform(val => val.trim()),

  email: z.string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address')
    .max(255, 'Email must be less than 255 characters')
    .transform(val => val.trim().toLowerCase()),

  password: z.string()
    .min(1, 'Password is required')
    .min(8, 'Password must be at least 8 characters')
    .max(128, 'Password must be less than 128 characters')
    .regex(/(?=.*[a-z])/, 'Password must contain at least one lowercase letter')
    .regex(/(?=.*[A-Z])/, 'Password must contain at least one uppercase letter')
    .regex(/(?=.*\d)/, 'Password must contain at least one number'),

  confirmPassword: z.string()
    .min(1, 'Please confirm your password'),

  agreeToTerms: z.boolean()
    .refine(val => val === true, 'You must agree to the terms and conditions')
}).refine(data => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword']
})

// Type inference
export type SignUpData = z.infer<typeof signUpSchema>

// Validation errors interface
export interface ValidationErrors {
  firstName?: string
  lastName?: string
  email?: string
  password?: string
  confirmPassword?: string
  agreeToTerms?: string
}

// Validation functions
export const validateField = (
  field: keyof SignUpData,
  signUpData: SignUpData,
  validationErrors: ValidationErrors
): ValidationErrors => {
  const newErrors = { ...validationErrors }

  try {
    // Create a partial schema for the specific field
    const fieldSchema = signUpSchema.pick({ [field]: true })

    // Special handling for confirmPassword since it depends on password
    if (field === 'confirmPassword') {
      signUpSchema.parse(signUpData)
      delete newErrors.confirmPassword
    } else if (field === 'password') {
      // Validate password field
      fieldSchema.parse({ [field]: signUpData[field] })
      delete newErrors.password

      // Also re-validate confirmPassword if it exists
      if (signUpData.confirmPassword) {
        try {
          signUpSchema.parse(signUpData)
          delete newErrors.confirmPassword
        } catch (error) {
          if (error instanceof z.ZodError) {
            const confirmPasswordError = error.issues.find(err => err.path.includes('confirmPassword'))
            if (confirmPasswordError) {
              newErrors.confirmPassword = confirmPasswordError.message
            }
          }
        }
      }
    } else {
      // Validate other fields normally
      fieldSchema.parse({ [field]: signUpData[field] })
      delete newErrors[field]
    }
  } catch (error) {
    if (error instanceof z.ZodError) {
      const fieldError = error.issues.find(err =>
        err.path.length === 1 && err.path[0] === field
      )
      if (fieldError) {
        newErrors[field] = fieldError.message
      }
    }
  }

  return newErrors
}

// Validate all fields
export const validateAllFields = (signUpData: SignUpData): { isValid: boolean; errors: ValidationErrors } => {
  try {
    signUpSchema.parse(signUpData)
    return { isValid: true, errors: {} }
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors: ValidationErrors = {}
      error.issues.forEach(err => {
        const fieldName = err.path[0] as keyof ValidationErrors
        if (fieldName) {
          errors[fieldName] = err.message
        }
      })
      return { isValid: false, errors }
    }
    return { isValid: false, errors: {} }
  }
}

// Password strength checker
export const getPasswordStrength = (password: string) => {
  if (!password) return []

  return [
    { label: 'At least 8 characters', valid: password.length >= 8 },
    { label: 'One lowercase letter', valid: /(?=.*[a-z])/.test(password) },
    { label: 'One uppercase letter', valid: /(?=.*[A-Z])/.test(password) },
    { label: 'One number', valid: /(?=.*\d)/.test(password) },
  ]
}
