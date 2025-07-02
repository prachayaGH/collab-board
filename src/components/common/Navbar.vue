<script setup lang="ts">
import { ref } from 'vue';
defineOptions({ name: "AppNavbar" });
import { useRouter } from 'vue-router';

const router = useRouter();

function goToLogin() {
  router.push('/login');
}

const isMenuOpen = ref(false)
</script>

<template>
  <nav class="relative flex flex-row justify-between h-15 items-center ">
    <div class="flex flex-row md:gap-40">
      <div class="flex flex-row gap-2 items-center cursor-pointer">
        <i class="fa-solid fa-comments md:text-2xl"></i>
        <h1 class="font-bold md:text-[24px]">CollabBoard</h1>
      </div>
      <!-- Desktop Menu -->
      <ul class="hidden md:flex flex-row md:gap-8 items-center">
        <li class="cursor-pointer">Features</li>
        <li class="cursor-pointer">Pricing</li>
        <li class="cursor-pointer">About</li>
      </ul>
    </div>
    <!-- Desktop Buttons -->
    <div class="hidden md:flex flex-row gap-3">
      <button
        @click="goToLogin"
        class="btn--primary h-10 w-23 rounded-[8px] cursor-pointer">Login</button>
      <button class="btn--secondary h-10 w-23 rounded-[8px] cursor-pointer">Sign&nbsp;Up</button>
    </div>
    <!-- Hamburger Menu Button (Mobile only) -->
    <button class="md:hidden" @click="isMenuOpen = !isMenuOpen">
      <i class="fa-solid fa-bars text-2xl cursor-pointer"></i>
    </button>
  </nav>
  <!-- Mobile Dropdown Menu -->
    <div v-if="isMenuOpen" class="mt-4 md:hidden absolute left-0 top-10 w-full bg-white shadow-lg px-10 pb-5 z-50 border-t-1 border-gray-200 flex flex-col">
      <ul class="flex flex-col my-3 text-center">
        <li class="cursor-pointer hover:bg-gray-200 active:text-[#6366F1] py-2">Features</li>
        <li class="cursor-pointer hover:bg-gray-200 active:text-[#6366F1] py-2">Pricing</li>
        <li class="cursor-pointer hover:bg-gray-200 active:text-[#6366F1] py-2">About</li>
      </ul>
      <div class="flex flex-col gap-2">
        <button class="btn--primary h-10 rounded-[8px] cursor-pointer">Login</button>
        <button class="btn--secondary h-10 rounded-[8px] cursor-pointer">SignUp</button>
      </div>
    </div>
</template>

<style scoped>
.fa-comments {
  color: #6366F1
}
</style>
