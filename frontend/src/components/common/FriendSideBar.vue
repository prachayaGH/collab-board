<script setup lang="ts">
</script>

<template>
  <div class="h-screen w-1/3 p-4">
    <div>
      <h4 class="text-[10px] font-bold text-gray-500 mb-3">ONLINE (5)</h4>
      <!-- map ชื่อเพื่อน -->
      <div class="flex items-center mb-2 gap-2 content-center p-2 button-ghost relative">
        <img
          src="https://hips.hearstapps.com/hmg-prod/images/white-cat-breeds-kitten-in-grass-67bf648a54a3b.jpg?crop=0.668xw:1.00xh;0.167xw,0&resize=640:*"
          alt="cat" class="w-6 h-6 rounded-full ">
        <!-- active รึเปล่า? -->
        <div class="bg-green-500 w-2 h-2 border-1 border-white rounded-full absolute bottom-1 left-6"></div>
        <p class="text-[14px]">John Smith</p>
      </div>
    </div>
    <h4 class="text-[10px] font-bold text-gray-500 mb-3">RECENT FILES</h4>
    <div class="flex flex-col">
      <!-- map ไฟล์ -->
      <div class="flex items-center gap-2 mb-4">
        <div class="bg-purple-500 w-7 h-7 text-center content-center text-[14px] rounded-[6px] text-white font-bold">T
        </div>
        <div class="content-center">
          <h4 class="text-[14px]">Project Brief.pdf</h4>
          <p class="text-[10px] text-gray-500">5 members online</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
