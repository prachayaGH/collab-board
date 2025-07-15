<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
defineOptions({ name: "AppNavbar" });

interface UserProfile {
  firstName: string;
  lastName: string;
  email: string;
  avatarUrl: string | null;
}

const router = useRouter();
const isMenuOpen = ref(false);
const isLoggedIn = ref(false);
const userProfile = ref<UserProfile | null>(null);
const isDropdownOpen = ref(false);

function getInitials(firstName?: string, lastName?: string): string {
  return (firstName?.[0] || "") + (lastName?.[0] || "");
}

async function fetchUserProfile() {
  try {
    const res = await axios.get(`${import.meta.env.VITE_API_URL}/me`, { withCredentials: true });
    const data = res.data;

    userProfile.value = {
      firstName: data.display_name?.split(" ")[0] || "",
      lastName: data.display_name?.split(" ")[1] || "",
      avatarUrl: data.avatar_url,
      email: data.email,
    };

    isLoggedIn.value = true;

  } catch (err) {
    if (axios.isAxiosError(err) && err.response?.status === 401) {
      const refreshed = await refreshAccessToken();
      if (refreshed) {
        return fetchUserProfile();
      }
    }
    isLoggedIn.value = false;
    userProfile.value = null;
  }
}

async function refreshAccessToken(): Promise<boolean> {
  try {
    const res = await axios.post(
      `${import.meta.env.VITE_API_URL}/refresh`,
      {},
      { withCredentials: true }
    );
    return true;
  } catch (error) {
    console.error("Refresh token failed", error);
    return false;
  }
}


function goToLogin() {
  router.push("/login");
}

function goToSignup() {
  router.push("/singup");
}

function logout() {
  axios.post(`${import.meta.env.VITE_API_URL}/logout`, {}, { withCredentials: true }).then(() => {
    isLoggedIn.value = false;
    userProfile.value = null;
    router.push("/");
  });
}

function goToEditProfile() {
  router.push("/account");
}

onMounted(fetchUserProfile);
</script>

<template>
  <nav class="relative flex flex-row justify-between h-15 items-center px-4">
    <div class="flex flex-row md:gap-40">
      <div class="flex flex-row gap-2 items-center cursor-pointer">
        <i class="fa-solid fa-comments md:text-2xl"></i>
        <h1 class="font-bold md:text-[24px]">CollabBoard</h1>
      </div>
      <ul v-if="!isLoggedIn" class="hidden md:flex flex-row md:gap-8 items-center">
        <li class="cursor-pointer">Features</li>
        <li class="cursor-pointer">Pricing</li>
        <li class="cursor-pointer">About</li>
      </ul>
    </div>

    <!-- Right: Desktop -->
    <div class="hidden md:flex flex-row gap-3 items-center">
      <template v-if="!isLoggedIn">
        <button @click="goToLogin" class="btn--primary h-10 w-23 rounded-[8px]">Login</button>
        <button @click="goToSignup" class="btn--secondary h-10 w-23 rounded-[8px]">Sign Up</button>
      </template>

      <template v-else>
        <div class="relative hidden md:block">
          <div
            @click="isDropdownOpen = !isDropdownOpen"
            class="flex items-center gap-3 cursor-pointer"
          >
            <div
              class="w-8 h-8 rounded-full bg-pink-300 flex items-center justify-center text-white font-bold text-sm overflow-hidden"
            >
              <img
                v-if="userProfile?.avatarUrl"
                :src="userProfile.avatarUrl"
                class="w-full h-full object-cover rounded-full"
              />
              <span v-else>
                {{ getInitials(userProfile?.firstName, userProfile?.lastName) }}
              </span>
            </div>
            <span class="font-medium"
              >{{ userProfile?.firstName }} {{ userProfile?.lastName }}</span
            >
            <i class="fa-solid fa-chevron-down text-sm text-gray-400"></i>
          </div>
          <div
            v-if="isDropdownOpen"
            class="absolute right-0 mt-2 bg-white rounded shadow-lg py-2 w-40 z-50"
          >
            <div @click="goToEditProfile" class="px-4 py-2 hover:bg-gray-100 cursor-pointer">
              Edit Profile
            </div>
            <div @click="logout" class="px-4 py-2 hover:bg-gray-100 cursor-pointer">Logout</div>
          </div>
        </div>
      </template>
    </div>

    <!-- Hamburger (only when NOT logged in) -->
    <button v-if="!isLoggedIn" class="md:hidden" @click="isMenuOpen = !isMenuOpen">
      <i class="fa-solid fa-bars text-2xl cursor-pointer"></i>
    </button>
    <template v-else>
      <div class="relative md:hidden">
        <div
          @click="isDropdownOpen = !isDropdownOpen"
          class="flex items-center gap-2 cursor-pointer"
        >
          <div
            class="w-8 h-8 rounded-full bg-pink-300 flex items-center justify-center text-white font-bold text-sm overflow-hidden"
          >
            <img
              v-if="userProfile?.avatarUrl"
              :src="userProfile.avatarUrl"
              class="w-full h-full object-cover rounded-full"
            />
            <span v-else>
              {{ getInitials(userProfile?.firstName, userProfile?.lastName) }}
            </span>
          </div>
          <i class="fa-solid fa-chevron-down text-sm text-gray-400"></i>
        </div>
        <div
          v-if="isDropdownOpen"
          class="absolute right-0 mt-2 bg-white rounded shadow-lg py-2 w-50 z-50"
        >
          <div @click="goToEditProfile" class="px-4 py-2 hover:bg-gray-100 cursor-pointer">
            Edit Profile
          </div>
          <div @click="logout" class="px-4 py-2 hover:bg-gray-100 cursor-pointer">Logout</div>
        </div>
      </div>
    </template>
  </nav>

  <!-- Mobile Dropdown -->
  <div
    v-if="!isLoggedIn && isMenuOpen"
    class="mt-4 md:hidden absolute left-0 top-16 w-full bg-white shadow-lg px-10 pb-5 z-50 border-t-1 border-gray-200 flex flex-col"
  >
    <ul class="flex flex-col my-3 text-center">
      <li class="cursor-pointer hover:bg-gray-200 py-2">Features</li>
      <li class="cursor-pointer hover:bg-gray-200 py-2">Pricing</li>
      <li class="cursor-pointer hover:bg-gray-200 py-2">About</li>
    </ul>

    <div class="flex flex-col gap-2">
      <button @click="goToLogin" class="btn--primary h-10 rounded-[8px]">Login</button>
      <button @click="goToSignup" class="btn--secondary h-10 rounded-[8px]">Sign Up</button>
    </div>
  </div>
</template>

<style scoped>
.fa-comments {
  color: #6366f1;
}
</style>
