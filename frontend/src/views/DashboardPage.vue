<script setup lang="ts">
import { ref } from 'vue'
import Navbar from "@/components/common/Navbar.vue";
import SideBar from "@/components/common/SideBar.vue";
import FriendSideBar from "@/components/common/FriendSideBar.vue";
import ChatWindow from "@/components/chat/ChatWindow.vue";
import type { User } from '@/types'

const selectedFriend = ref<User | null>(null)

const handleOpenChat = (friend: User) => {
  selectedFriend.value = friend
  console.log('Opening chat with:', friend.display_name)
}

</script>

<template>
  <div class="md:px-25 px-10 border-2 border-gray-200 bg-white sticky top-0 z-50">
    <Navbar />
  </div>

  <div class="flex ">
    <SideBar />

    <div class="bg-gray-100 w-full h-screen">

      <!-- Show ChatWindow when friend is selected -->
      <ChatWindow
        v-if="selectedFriend"
        :friend="selectedFriend"
        @closeChat="selectedFriend = null"
      />

      <!-- Default content when no chat is open -->
      <div v-else class="flex items-center justify-center h-full text-gray-500">
        <div class="text-center">
          <h2 class="text-xl mb-2">Select a friend to start chatting</h2>
          <p>Click on a friend's name from the sidebar to open a chat window</p>
        </div>
      </div>
    </div>

    <!-- Pass the openChat handler to FriendSideBar -->
    <FriendSideBar @openChat="handleOpenChat" />
  </div>
</template>
