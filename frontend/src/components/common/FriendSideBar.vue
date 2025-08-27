<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useApi } from "@/composables/useApi";

const {
  getFriends,
  getPendingRequests,
} = useApi();

const emit = defineEmits(['openChat']);

const pendingRequests = ref<any[]>([]);
const friends = ref<any[]>([]);

const fetchPendingRequests = async () => {
  try {
    const result = await getPendingRequests();
    pendingRequests.value = result;
    console.log("Pending Requests:", result);
  } catch (error) {
    console.error("Error fetching pending requests:", error);
  }
};

const fetchFriends = async () => {
  try {
    const result = await getFriends();
    friends.value = result;
    console.log("Friends:", result);
  } catch (error) {
    console.error("Error fetching friends:", error);
  }
};

onMounted(() => {
  fetchPendingRequests();
  fetchFriends();
});


function getInitials(name: string | undefined): string {
  if (!name) return "?";
  const parts = name.trim().split(" ");
  // ถ้ามีทั้ง first + last name → เอา 2 ตัว
  if (parts.length > 1) {
    return parts[0][0].toUpperCase() + parts[1][0].toUpperCase();
  }
  // ถ้ามีชื่อเดียว → เอาตัวแรก
  return parts[0][0].toUpperCase();
}

async function respond(requestId: number, action: "accept" | "decline") {
  try {
    await useApi().respondToFriendRequest(requestId, action);
  } catch (error) {
    console.error("Respond to friend request error:", error);
  }
}

function openChatWithFriend(friend: any) {
  emit('openChat', friend);
}

</script>

<template>
  <div class="h-screen w-1/3 p-4">
    <div>
      <h4 class="text-[10px] font-bold text-gray-500 mb-3">FRIEND REQUEST  ({{ pendingRequests.length }})</h4>
      <div
        v-for="request in pendingRequests"
        :key="request.id"
        class="flex items-center mb-2 gap-2 content-center p-2 button-ghost relative"
      >
        <div class="w-8 h-8 rounded-full bg-pink-300 flex items-center justify-center text-white font-bold text-sm ">
          <img
            v-if="request.requester?.avatarUrl"
            :src="request.requester.avatarUrl"
            :alt="request.requester.display_name"
            class="w-full h-full object-cover rounded-full"
          />
          <span v-else>
            {{ getInitials(request.requester?.display_name) }}
          </span>
        </div>
        <p class="text-[14px] hidden md:block">{{ request.requester.display_name }}</p>

        <!-- ปุ่ม Accept / Decline -->
         <div class="flex gap-2">
          <button
            @click="respond(request.id, 'accept')"
            class="px-2 py-1 text-[10px] bg-green-500 text-white rounded-md hover:bg-green-600"
          >
            Accept
          </button>
          <button
            @click="respond(request.id, 'decline')"
            class="px-2 py-1 text-xs bg-red-500 text-white rounded-md hover:bg-red-600"
          >
            Decline
          </button>
        </div>
      </div>

      <h4 class="text-[10px] font-bold text-gray-500 mb-3">ONLINE ({{ friends.length}})</h4>

      <!-- map ชื่อเพื่อน -->
      <div
        v-for="friend in friends"
        :key="friend.id"
        class="flex items-center mb-2 gap-2 content-center p-2 button-ghost relative"
        @click="openChatWithFriend(friend)"
      >
        <div class="w-8 h-8 rounded-full bg-pink-300 flex items-center justify-center text-white font-bold text-sm overflow-hidden">
          <img
            v-if="friend.avatar_url"
            :src="friend.avatar_url"
            :alt="friend.display_name"
            class="w-full h-full object-cover rounded-full"
          />
          <span v-else>
            {{ getInitials(friend.display_name) }}
          </span>
        </div>
        <!-- active รึเปล่า? -->
        <div
          class="w-2 h-2 border-1 border-white rounded-full absolute bottom-1 left-8"
          :class="friend.status === 'online' ? 'bg-green-500' : 'bg-gray-500'"
        ></div>
        <p class="text-[14px]">{{ friend.display_name }}</p>
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
