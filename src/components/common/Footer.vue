<script setup lang="ts">
defineOptions({ name: "AppFooter" });
</script>

<template>
  <footer class="bg-[#1F2937] text-white p-8 px-25">
    <div class="md:grid md:grid-cols-4 grid grid-cols-1 mb-15 gap-6">
      <ul>
        <li class="flex flex-row gap-2 items-center mb-5">
          <i class="fa-solid fa-comments text-[20px]"></i>
          <h4 class="font-bold text-[20px]">CollabBpard</h4>
        </li>
        <li class="text-gray-400">Real-time collaboration platform for modern teams.</li>
      </ul>
      <ul class="text-[14px]">
        <li class="font-bold mb-5">Product</li>
        <li class="mb-2 text-gray-400">Features</li>
        <li class="mb-2 text-gray-400">Pricing</li>
        <li class="text-gray-400">Security</li>
      </ul>
      <ul class="text-[14px]">
        <li class="font-bold mb-5">Company</li>
        <li class="mb-2 text-gray-400">About</li>
        <li class="mb-2 text-gray-400">Blog</li>
        <li class="text-gray-400">Careers</li>
      </ul>
      <ul class="text-[14px]">
        <li class="font-bold mb-5">Support</li>
        <li class="mb-2 text-gray-400">Help Center</li>
        <li class="mb-2 text-gray-400">Contact</li>
        <li class="text-gray-400">Privacy Policy</li>
      </ul>
    </div>
    <hr class="text-gray-700">
    <p class="text-center text-[14px] text-gray-400 mt-5">© 2024 CollabChat. All rights reserved.</p>
  </footer>
</template>

<style scoped>

.fa-comments {
  color: #6366F1
}

</style>
