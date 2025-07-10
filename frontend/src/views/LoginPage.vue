<script setup lang="ts">
import { ref, reactive } from "vue";
import Navbar from "@/components/common/Navbar.vue";
import { LoginValidator, loginSchema, type LoginData, type ValidationErrors } from "@/schemas/loginSchema";
import axios from "axios";
import { useRouter } from "vue-router";
import { authService } from "@/utils/auth";

const loginData = reactive<LoginData>({
  email: "",
  password: "",
});

const errors = reactive<ValidationErrors>({});
const isLoading = ref(false);
const showPassword = ref(false);
const router = useRouter();

const clearError = (field: keyof ValidationErrors) => {
  if (errors[field]) {
    delete errors[field];
  }
};

const validateField = (field: keyof LoginData, value: string) => {
  const error = LoginValidator.validateField(field, value);
  if (error) {
    errors[field] = error;
  } else {
    clearError(field);
  }
};

const validateForm = (): boolean => {
  const { isValid, errors: validationErrors } = LoginValidator.validateForm(loginData);

  // Clear existing errors
  Object.keys(errors).forEach((key) => {
    delete errors[key as keyof ValidationErrors];
  });

  // Set new errors
  Object.assign(errors, validationErrors);

  return isValid;
};

const handleSubmit = async () => {
  const isValid = validateForm();

  if (!isValid) {
    return;
  }

  isLoading.value = true;

  const validatedData = loginSchema.parse(loginData);

  try {
    const response = await axios(`${import.meta.env.VITE_API_URL}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      withCredentials: true, // ✅ สำคัญมาก!
      data: {
        email: validatedData.email,
        password: validatedData.password,
      },
    })

    const data = response.data;

    if (response.status < 200 || response.status >= 300) {
      throw new Error(data.detail || "Login failed");
    }
    if (data.redirect_url) {
      router.replace(data.redirect_url); // ⬅️ ใช้ URL ที่ backend ให้มา
    }
  } catch (error) {
    alert(error);
  } finally {
    isLoading.value = false;
  }
};

const googleLogin = async () => {
  authService.loginWithGoogle();
  window.location.href = `${import.meta.env.VITE_API_URL}/auth/google/login`;
};

const togglePassword = () => {
  showPassword.value = !showPassword.value;
};

const handleInputChange = (field: keyof LoginData, value: string) => {
  loginData[field] = value;
  clearError(field);
};

const handleInputBlur = (field: keyof LoginData) => {
  validateField(field, loginData[field]);
};
</script>

<template>
  <div class="md:px-25 px-10 border-2 border-gray-200 bg-white sticky top-0 z-50">
    <Navbar />
  </div>
  <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">
    <div class="max-w-md w-full space-y-8">
      <!-- Header -->
      <div class="text-center animate-fade-in">
        <div
          class="mx-auto h-12 w-12 flex items-center justify-center rounded-[8px] bg-[#6366F1] mb-6"
        >
          <i class="fa-solid fa-lock text-white text-xl"></i>
        </div>
        <h2 class="text-3xl font-bold text-gray-900 mb-2">Welcome back</h2>
        <p class="text-gray-600">Sign in to your account</p>
      </div>

      <!-- Login Form -->
      <div class="bg-white py-8 px-6 shadow-lg rounded-lg border border-gray-200 animate-slide-up">
        <form class="space-y-6" @submit.prevent="handleSubmit">
          <!-- Email Field -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              Email address
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autocomplete="email"
              v-model="loginData.email"
              @input="handleInputChange('email', ($event.target as HTMLInputElement).value)"
              @blur="handleInputBlur('email')"
              :class="[
                'input-field w-full border-1 py-1 rounded-[4px] transition-colors',
                errors.email
                  ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
                  : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500',
              ]"
              placeholder=" Enter your email"
            />
            <div v-if="errors.email" class="mt-1 text-sm text-red-600">
              {{ errors.email }}
            </div>
          </div>

          <!-- Password Field -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <div class="relative">
              <input
                id="password"
                name="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                v-model="loginData.password"
                @input="handleInputChange('password', ($event.target as HTMLInputElement).value)"
                @blur="handleInputBlur('password')"
                :class="[
                  'input-field pr-12 w-full border-1 py-1 rounded-[4px] transition-colors',
                  errors.password ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
                ]"
                placeholder=" Enter your password"
              />
              <button
                type="button"
                @click="togglePassword"
                class="cursor-pointer absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg
                  v-if="!showPassword"
                  class="h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
                <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"
                  />
                </svg>
              </button>
            </div>
             <div v-if="errors.password" class="mt-1 text-sm text-red-600">
              {{ errors.password }}
            </div>
          </div>

          <!-- Remember Me & Forgot Password -->
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                class="h-4 w-4 text-gray-900 focus:ring-gray-500 border-gray-300 rounded"
              />
              <label for="remember-me" class="ml-2 block text-sm text-gray-700">
                Remember me
              </label>
            </div>

            <div class="text-sm">
              <a
                href="#"
                class="text-[#6366F1] hover:text-[#696CFF] active:text-[#595CD9] transition-colors"
              >
                Forgot password?
              </a>
            </div>
          </div>

          <!-- Submit Button -->
          <div class="text-center">
            <button
              type="submit"
              :disabled="isLoading"
              class="btn--primary w-full h-10 rounded-[8px]"
            >
              <span v-if="!isLoading">Login</span>
              <div v-else class="flex items-center justify-center">
                <svg
                  class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    class="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="4"
                  ></circle>
                  <path
                    class="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Login...
              </div>
            </button>
          </div>
        </form>

        <!-- Divider -->
        <div class="mt-6">
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-300" />
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-2 bg-white text-gray-500">Or continue with</span>
            </div>
          </div>

          <!-- Social Login -->
          <div class="mt-6 text-center">
            <button
              @click="googleLogin"
              class="w-full border-1 py-3 rounded-[8px] border-gray-300 cursor-pointer"
            >
              <div class="flex items-center justify-center">
                <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
                  <path
                    fill="currentColor"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="currentColor"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                Continue with Google
              </div>
            </button>
          </div>
        </div>

        <!-- Sign Up Link -->
        <div class="mt-6 text-center">
          <p class="text-sm text-gray-600">
            Don't have an account?
            <a href="#" class="font-medium purple-200 hover:purple-300 transition-colors">
              Sign up
            </a>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
