<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { useSocket } from "@/composables/useSocket";
import { useApi } from "@/composables/useApi";
import type { User, FriendRequest } from "@/types";
import { debounce } from "lodash-es";

const emit = defineEmits<{
  "start-chat": [friend: User];
}>();

const {
  friends,
  pendingRequests,
  sendFriendRequest: socketSendFriendRequest,
  respondToFriendRequest,
} = useSocket();
const api = useApi();

const searchQuery = ref("");
const searchResults = ref<User[]>([]);
const showAddFriendModal = ref(false);

const handleSearch = debounce(async () => {
  if (searchQuery.value.length < 2) {
    searchResults.value = [];
    return;
  }

  try {
    searchResults.value = await api.searchUsers(searchQuery.value);
    console.log("Search results:", searchResults.value);
  } catch (error) {
    console.error("Search error:", error);
  }
}, 300);

const closeModal = () => {
  showAddFriendModal.value = false;
  searchQuery.value = "";
  searchResults.value = [];
};

const sendFriendRequest = async (email: string) => {
  try {
    socketSendFriendRequest(email);
    searchResults.value = [];
    searchQuery.value = "";

  } catch (error) {
    console.error("Friend request error:", error);
  }
};

</script>

<template>
  <div class="h-screen w-1/3 p-4">
    <div class="flex flex-col justify-between h-full">
      <div class="">
        <!-- ซ่อนถ้ายังไม่ได้กดสร้างห้องแชท -->
        <div class="flex items-center gap-2 mb-4">
          <div
            class="bg-purple-500 w-8 h-8 text-center content-center text-[14px] rounded-[6px] text-white font-bold"
          >
            T
          </div>
          <div class="content-center">
            <h4>Team Workspace</h4>
            <p class="text-[10px] text-gray-500">5 members online</p>
          </div>
        </div>
        <hr class="text-gray-200" />
        <div class="mt-4">
          <h4 class="text-[10px] font-bold text-gray-500 mb-3">CHANNELS</h4>
          <!-- map ชื่อห้องแชท -->
          <div class="flex items-center mb-2 gap-3 content-center p-2 button-ghost">
            <p class="text-[14px]"># general</p>
            <p class="text-[10px] bg-blue-500 text-white w-4 h-4 text-center rounded-2xl">2</p>
          </div>
          <div class="flex items-center mb-2 gap-3 content-center p-2 button-ghost">
            <p class="text-[14px]"># development</p>
            <p class="text-[10px] bg-blue-500 text-white w-4 h-4 text-center rounded-2xl">2</p>
          </div>
        </div>
        <div>
          <h4 class="text-[10px] font-bold text-gray-500 mb-3">DIRECT MESSAGES</h4>
          <!-- map ชื่อเพื่อน -->
          <div class="flex items-center mb-2 gap-2 content-center p-2 button-ghost relative">
            <img
              src="https://hips.hearstapps.com/hmg-prod/images/white-cat-breeds-kitten-in-grass-67bf648a54a3b.jpg?crop=0.668xw:1.00xh;0.167xw,0&resize=640:*"
              alt="cat"
              class="w-6 h-6 rounded-full"
            />
            <!-- active รึเปล่า? -->
            <div
              class="bg-green-500 w-2 h-2 border-1 border-white rounded-full absolute bottom-1 left-6"
            ></div>
            <p class="text-[14px]">John Smith</p>
            <p class="bg-red-500 text-white text-[10px] w-4 h-4 text-center rounded-full">2</p>
          </div>
          <div class="flex items-center mb-2 gap-2 content-center p-2 button-ghost relative">
            <img
              src="https://hips.hearstapps.com/hmg-prod/images/white-cat-breeds-kitten-in-grass-67bf648a54a3b.jpg?crop=0.668xw:1.00xh;0.167xw,0&resize=640:*"
              alt="cat"
              class="w-6 h-6 rounded-full"
            />
            <!-- active รึเปล่า? -->
            <div
              class="bg-green-500 w-2 h-2 border-1 border-white rounded-full absolute bottom-1 left-6"
            ></div>
            <p class="text-[14px]">John Smith</p>
          </div>
        </div>
      </div>
      <div class="flex flex-col gap-2">
        <button
          @click="showAddFriendModal = true"
          class="border-1 border-dashed border-gray-300 p-3 rounded-[6px] text-gray-600 text-center text-[14px] hover:bg-gray-100 cursor-pointer"
        >
          + Add Friend
        </button>

        <button
          class="p-3 rounded-[6px] text-white text-center text-[14px] bg-blue-400 hover:bg-blue-500 cursor-pointer"
        >
          + Add Channel
        </button>
      </div>
    </div>
  </div>

  <!-- Add Friend Modal -->
  <transition name="fade">
    <div
      v-if="showAddFriendModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
    >
      <!-- Modal box -->
      <div class="bg-white w-120 p-6 rounded-2xl shadow-xl relative">
        <!-- ปุ่มปิด -->
        <button
          class="absolute top-3 right-3 text-gray-400 hover:text-gray-600 text-xl cursor-pointer"
          @click="closeModal"
        >
          X
        </button>

        <h2 class="text-lg font-bold mb-4 text-gray-800">Search Friend</h2>

        <!-- ช่องค้นหา -->
        <input
          v-model="searchQuery"
          @input="handleSearch"
          type="text"
          placeholder="Search users by email or name..."
          class="w-full border border-gray-300 rounded-lg px-4 py-2 mb-4 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />

        <!-- ตัวอย่างผลลัพธ์ -->
        <div
          v-if="searchResults.length > 0"
          class="w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg"
        >
          <div
            v-for="user in searchResults"
            :key="user.id"
            class="p-3 hover:bg-gray-50 cursor-pointer flex items-center justify-between"
          >
            <div class="flex items-center space-x-3">
              <img
                :src="user.avatar_url || '/default-avatar.png'"
                :alt="user.display_name"
                class="w-8 h-8 rounded-full"
              />
              <div>
                <div class="font-medium">{{ user.display_name }}</div>
                <div class="text-sm text-gray-500">{{ user.email }}</div>
              </div>
            </div>
            <button
              @click="sendFriendRequest(user.email)"
              :class="{
                'bg-blue-500 text-white hover:bg-blue-600 p-2 rounded-[8px] cursor-pointer': user.relationship === 'none',
                'bg-gray-300 text-gray-600 p-2 rounded-[8px]': user.relationship !== 'none',
              }"
              :disabled="user.relationship !== 'none'"
            >
              Add Friend
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped></style>
