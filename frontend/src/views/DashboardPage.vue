<script setup lang="ts">
import Navbar from "@/components/common/Navbar.vue";
import SideBar from "@/components/common/SideBar.vue";
import FriendSideBar from "@/components/common/FriendSideBar.vue";
import ChatWindow from "@/components/chat/ChatWindow.vue";
</script>

<template>
  <div class="md:px-25 px-10 border-2 border-gray-200 bg-white sticky top-0 z-50">
    <Navbar />
  </div>

  <div class="flex ">
    <SideBar />

    <div class="bg-gray-100 w-full h-screen">
      <ChatWindow />
    </div>

    <FriendSideBar />
  </div>
</template>
