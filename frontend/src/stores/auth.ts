import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authService } from '@/utils/auth'

interface UserProfile {
  id: number;
  firstName: string;
  lastName: string;
  email: string;
  avatarUrl: string | null;
}

export const useAuthStore = defineStore('me', () => {
  const user = ref<UserProfile | null>(null)
  const isLoading = ref(false)

  const fetchUser = async () => {
    try {
      isLoading.value = true
      const data = await authService.getCurrentUser()
      user.value = data
    } catch (error) {
      console.error('Fetch user error:', error)
      user.value = null
    } finally {
      isLoading.value = false
    }
  }

  const loginWithGoogle = () => {
    authService.loginWithGoogle()
  }

  const logout = async () => {
    await authService.logout()
    user.value = null
    window.location.href = '/'
  }

  return {
    user,
    isLoading,
    fetchUser,
    loginWithGoogle,
    logout,
  }
})
