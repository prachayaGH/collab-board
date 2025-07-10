<script setup lang="ts">
import { ref, reactive, computed } from "vue";
import Navbar from "@/components/common/Navbar.vue";
import axios from "axios";
import { authService } from "@/utils/auth";
import { useRouter } from "vue-router";
import {
  signUpSchema,
  type ValidationErrors,
  validateField,
  validateAllFields,
  getPasswordStrength,
} from "@/schemas/signUpSchema";

interface SignUpData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
  agreeToTerms: boolean;
}

const signUpData = reactive<SignUpData>({
  firstName: "",
  lastName: "",
  email: "",
  password: "",
  confirmPassword: "",
  agreeToTerms: false,
});

const isLoading = ref(false);
const showPassword = ref(false);
const showConfirmPassword = ref(false);
const validationErrors = ref<ValidationErrors>({});
const router = useRouter();

// Computed properties
const passwordStrength = computed(() => getPasswordStrength(signUpData.password));

const passwordsMatch = computed(() => {
  return signUpData.password === signUpData.confirmPassword || signUpData.confirmPassword === "";
});

const isFormValid = computed(() => {
  return (
    signUpData.firstName &&
    signUpData.lastName &&
    signUpData.email &&
    signUpData.password &&
    signUpData.confirmPassword &&
    passwordsMatch.value &&
    signUpData.agreeToTerms
  );
});

// Methods
const handleFieldValidation = (field: keyof SignUpData) => {
  validationErrors.value = validateField(field, signUpData, validationErrors.value);
};

const getInputClass = (
  field: keyof SignUpData,
  baseClass: string = "input-field w-full border-1 py-1 border-gray-300 rounded-[4px]"
) => {
  if (validationErrors.value[field]) {
    return `${baseClass} border-red-500 focus:ring-red-500 focus:border-red-500`;
  }
  return baseClass;
};

const handleSubmit = async () => {
  const validation = validateAllFields(signUpData);

  if (!isFormValid.value) {
    validationErrors.value = validation.errors;
    return;
  }

  isLoading.value = true;

  try {
    const validatedData = signUpSchema.parse(signUpData);

    const response = await axios(`${import.meta.env.VITE_API_URL}/signup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      data: {
        email: validatedData.email,
        password: validatedData.password,
        display_name: `${validatedData.firstName} ${validatedData.lastName}`,
        oauth_provider: "local",
        oauth_id: null,
        avatar_url: null,
      },
    });

    const data = response.data;

    if (response.status < 200 || response.status >= 300) {
      throw new Error(data.detail || "Registration failed");
    }
    router.replace({ name: "Login" });
  } catch (error: any) {
    console.error(error);
    if (error.response?.status === 400 && error.response?.data?.detail?.includes("email")) {
      validationErrors.value.email = "This email is already registered";
    } else {
      alert(error.message || "Something went wrong");
    }
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

const toggleConfirmPassword = () => {
  showConfirmPassword.value = !showConfirmPassword.value;
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
          <i class="fa-solid fa-user-plus text-white text-xl"></i>
        </div>
        <h2 class="text-3xl font-bold text-gray-900 mb-2">Create your account</h2>
        <p class="text-gray-600">Join us and get started today</p>
      </div>

      <!-- Sign Up Form -->
      <div class="bg-white py-8 px-6 shadow-lg rounded-lg border border-gray-200 animate-slide-up">
        <form class="space-y-6" @submit.prevent="handleSubmit">
          <!-- Name Fields -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="firstName" class="block text-sm font-medium text-gray-700 mb-2">
                First name
              </label>
              <input
                id="firstName"
                name="firstName"
                type="text"
                autocomplete="given-name"
                required
                v-model="signUpData.firstName"
                @blur="handleFieldValidation('firstName')"
                @input="handleFieldValidation('firstName')"
                :class="getInputClass('firstName')"
                class="input-field w-full border-1 py-1 border-gray-300 rounded-[4px]"
                placeholder=" First name"
              />
              <p v-if="validationErrors.firstName" class="mt-1 text-sm text-red-600">
                {{ validationErrors.firstName }}
              </p>
            </div>
            <div>
              <label for="lastName" class="block text-sm font-medium text-gray-700 mb-2">
                Last name
              </label>
              <input
                id="lastName"
                name="lastName"
                type="text"
                autocomplete="family-name"
                required
                v-model="signUpData.lastName"
                @blur="handleFieldValidation('lastName')"
                @input="handleFieldValidation('lastName')"
                :class="getInputClass('lastName')"
                class="input-field w-full border-1 py-1 border-gray-300 rounded-[4px]"
                placeholder=" Last name"
              />
              <p v-if="validationErrors.lastName" class="mt-1 text-sm text-red-600">
                {{ validationErrors.lastName }}
              </p>
            </div>
          </div>

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
              required
              v-model="signUpData.email"
              @blur="handleFieldValidation('email')"
              @input="handleFieldValidation('email')"
              :class="getInputClass('email')"
              class="input-field w-full border-1 py-1 border-gray-300 rounded-[4px]"
              placeholder=" Enter your email"
            />
            <p v-if="validationErrors.email" class="mt-1 text-sm text-red-600">
              {{ validationErrors.email }}
            </p>
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
                autocomplete="new-password"
                required
                v-model="signUpData.password"
                @blur="handleFieldValidation('password')"
                @input="handleFieldValidation('password')"
                :class="getInputClass('password')"
                class="input-field w-full border-1 py-1 border-gray-300 rounded-[4px]"
                placeholder=" Create a password"
              />
              <button
                type="button"
                @click="togglePassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors cursor-pointer"
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
            <p v-if="validationErrors.password" class="mt-1 text-sm text-red-600">
              {{ validationErrors.password }}
            </p>
            <div
              v-if="signUpData.password && !validationErrors.password"
              class="mt-2 text-xs text-gray-500"
            >
              <p>Password requirements:</p>
              <ul class="list-disc list-inside mt-1 space-y-1">
                <li
                  v-for="requirement in passwordStrength"
                  :key="requirement.label"
                  :class="requirement.valid ? 'text-green-600' : 'text-gray-400'"
                >
                  {{ requirement.label }}
                </li>
              </ul>
            </div>
          </div>

          <!-- Confirm Password Field -->
          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-2">
              Confirm password
            </label>
            <div class="relative">
              <input
                id="confirmPassword"
                name="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                autocomplete="new-password"
                required
                v-model="signUpData.confirmPassword"
                @blur="handleFieldValidation('confirmPassword')"
                :class="[
                  'input-field w-full border-1 py-1 border-gray-300 rounded-[4px]',
                  !passwordsMatch && signUpData.confirmPassword
                    ? 'border-red-300 focus:ring-red-500'
                    : '',
                ]"
                placeholder=" Confirm your password"
              />
              <button
                type="button"
                @click="toggleConfirmPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors cursor-pointer"
              >
                <svg
                  v-if="!showConfirmPassword"
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
            <p
              v-if="!passwordsMatch && signUpData.confirmPassword"
              class="mt-1 text-sm text-red-600"
            >
              {{ validationErrors.confirmPassword }}
            </p>
          </div>

          <!-- Terms and Conditions -->
          <div class="flex items-start">
            <div class="flex items-center h-5">
              <input
                id="agreeToTerms"
                name="agreeToTerms"
                type="checkbox"
                v-model="signUpData.agreeToTerms"
                @change="handleFieldValidation('agreeToTerms')"
                :class="[
                  'h-4 w-4 text-gray-900 focus:ring-gray-500 border-gray-300 rounded',
                  validationErrors.agreeToTerms ? 'border-red-500' : '',
                ]"
              />
            </div>
            <div class="ml-3 text-sm">
              <label for="agreeToTerms" class="text-gray-700">
                I agree to the
                <a href="#" class="text-gray-900 hover:text-gray-700 font-medium transition-colors">
                  Terms and Conditions
                </a>
                and
                <a href="#" class="text-gray-900 hover:text-gray-700 font-medium transition-colors">
                  Privacy Policy
                </a>
              </label>
            </div>
            <p v-if="validationErrors.agreeToTerms" class="mt-1 text-sm text-red-600">
              {{ validationErrors.agreeToTerms }}
            </p>
          </div>

          <!-- Submit Button -->
          <div>
            <button
              type="submit"
              :disabled="isLoading || !isFormValid"
              :class="[
                'w-full h-10 rounded-[8px] transition-colors',
                isFormValid && !isLoading
                  ? 'btn--primary'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              ]"
            >
              <span v-if="!isLoading">Create account</span>
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
                Creating account...
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

          <!-- Social Sign Up -->
          <div class="mt-6">
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

        <!-- Sign In Link -->
        <div class="mt-6 text-center">
          <p class="text-sm text-gray-600">
            Already have an account?
            <a href="#" class="font-medium text-gray-900 hover:text-gray-700 transition-colors">
              Sign in
            </a>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
