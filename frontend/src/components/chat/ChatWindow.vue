<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useSocket } from '@/composables/useSocket';
import { useAuthStore } from '@/stores/auth';
import type { User, Message } from '@/types';
import { useApi } from '@/composables/useApi';

interface Props {
  friend: User;
}

const props = defineProps<Props>();
const emit = defineEmits(['closeChat'])

const authStore = useAuthStore();
const socket = useSocket();
const api = useApi();

const newMessage = ref('');
const messagesContainer = ref<HTMLElement>();
const messageInput = ref<HTMLTextAreaElement>();

const currentUserId = computed(() => authStore.user?.id);

// เก็บประวัติแชทจาก API
const historyMessages = ref<Message[]>([]);
// ข้อความจาก socket (real-time)
const liveMessages = computed(() => socket.getChatMessages(props.friend.id) || []);
// รวม messages ทั้งหมด
const messages = computed(() => {
  return [...historyMessages.value, ...liveMessages.value];
});

// โหลดประวัติแชท
const loadChatHistory = async () => {
  if (!props.friend?.id) return;
  try {
    const data = await api.getChatHistory(props.friend.id, 50);
    historyMessages.value = data;
    await nextTick();
    scrollToBottom();
  } catch (err) {
    console.error("Error loading chat history:", err);
  }
};

// Debug: Check socket connection
watch(() => socket.connected, (isConnected) => {
  console.log('Socket connected:', isConnected);
});

// Join chat room when component mounts
onMounted(async () => {
  if (props.friend?.id) {
    console.log('Joining chat with friend ID:', props.friend.id);
    socket.joinChat(props.friend.id);

    await loadChatHistory();

    // Mark messages as read when opening chat
    socket.markMessagesRead(props.friend.id);

    // Focus on input
    nextTick(() => {
      messageInput.value?.focus();
    });
  }
});

// Scroll to bottom when new messages arrive
watch(() => messages.value.length, (newLength, oldLength) => {

  if (newLength > oldLength) {
    nextTick(() => {
      scrollToBottom();
    });
  }
});

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const sendMessage = () => {
  const content = newMessage.value.trim();

  if (!content || !props.friend?.id) {
    console.log('Cannot send: missing content or friend ID');
    return;
  }

  if (!socket.connected) {
    console.log('Cannot send: socket not connected');
    return;
  }

  socket.sendMessage(props.friend.id, content);
  newMessage.value = '';

  // Auto-resize textarea
  if (messageInput.value) {
    messageInput.value.style.height = 'auto';
  }
};

const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }

  // Auto-resize textarea
  nextTick(() => {
    if (messageInput.value) {
      messageInput.value.style.height = 'auto';
      messageInput.value.style.height = messageInput.value.scrollHeight + 'px';
    }
  });
};

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp);
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const messageDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

  const timeFormat = date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  });

  if (messageDate.getTime() === today.getTime()) {
    return timeFormat;
  } else {
    return `${date.toLocaleDateString()} ${timeFormat}`;
  }
};

// Mark messages as read when chat is visible
let readInterval: number;
onMounted(() => {
  readInterval = setInterval(() => {
    if (props.friend?.id) {
      socket.markMessagesRead(props.friend.id);
    }
  }, 2000);
});

onUnmounted(() => {
  if (readInterval) {
    clearInterval(readInterval);
  }
});

</script>

<template>
  <div class="chat-window flex flex-col h-full border-l-1 border-r-1 border-gray-200">
    <!-- Debug info (เอาออกได้เมื่อใช้งานจริง) -->
    <div class="bg-yellow-100 p-2 text-xs">
      <div>Socket connected: {{ socket.connected }}</div>
      <div>Current user: {{ currentUserId }}</div>
      <div>Friend ID: {{ friend.id }}</div>
      <div>Messages count: {{ messages.length }}</div>
    </div>

    <!-- Chat Header -->
    <div
      class="chat-header flex items-center justify-between p-4 border-b border-gray-200 bg-white"
    >
      <div class="flex items-center space-x-3">
        <button
          @click="$emit('closeChat')"
          class="md:hidden p-2 hover:bg-gray-100 rounded-full cursor-pointer"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 19l-7-7 7-7"
            ></path>
          </svg>
        </button>
        <div
          class="relative" v-if="friend"
        >
          <img
            :src="friend.avatar_url || '/default-avatar.png'"
            :alt="friend.display_name"
            class="w-8 h-8 rounded-full"
          />
          <div
            class="absolute -bottom-1 -right-0 w-3 h-3 rounded-full border-2 border-white"
            :class="friend.status === 'online' ? 'bg-green-500' : 'bg-gray-500'"
          ></div>
        </div>
        <div>
          <div class="font-medium">{{ friend.display_name }} [chat]</div>
          <div class="text-sm text-gray-500">{{ friend.status === 'online' ? 'Online' : 'Offline' }}</div>
        </div>
      </div>
      <div class="flex items-center space-x-4">
        <i class="fas fa-phone text-gray-600 cursor-pointer hover:text-gray-500"></i>
        <i class="fas fa-video text-gray-600 cursor-pointer hover:text-gray-500"></i>
        <i class="fas fa-exclamation-circle text-gray-600 cursor-pointer hover:text-gray-500"></i>
      </div>
    </div>

    <!-- Messages Area -->
    <div ref="messagesContainer"
      class="messages-container flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">

      <!-- แสดงเมื่อไม่มีข้อความ -->
      <div v-if="messages.length === 0" class="text-center text-gray-500 py-8">
        No messages yet. Start a conversation!
      </div>

      <div
        v-for="message in messages"
        :key="message.id"
        class="message"
        :class="{
          'own-message': message.sender_id === currentUserId,
          'friend-message': message.sender_id !== currentUserId
        }"
      >
        <div class="message-content">
          <p>{{ message.content }}</p>
          <div class="message-meta">
            <span class="time">{{ formatTime(message.created_at) }}</span>
            <span
              v-if="message.sender_id === currentUserId"
              class="read-status"
              :class="{ 'read': message.is_read }"
            >
              {{ message.is_read ? '✓✓' : '✓' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Message Input -->
    <div class="message-input p-4 border-t border-gray-200 bg-white">
      <div class="flex space-x-4">
        <i class="fa-solid fa-paperclip items-center content-center p-1"></i>
        <input
          v-model="newMessage"
          @keydown="handleKeyDown"
          type="text"
          placeholder="Type a message..."
          rows="1"
          ref="messageInput"
          class="flex-1 px-4 py-2 border border-gray-300 rounded-[8px] focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        <button
          @click="sendMessage"
          :disabled="!newMessage.trim()"
          class="p-2 w-10 bg-blue-500 text-white rounded-[8px] hover:bg-blue-600 cursor-pointer disabled:opacity-50"
        >
          <i class="fa-solid fa-paper-plane"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.own-message {
  display: flex;
  justify-content: flex-end;
}

.friend-message {
  display: flex;
  justify-content: flex-start;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
}

.own-message .message-content {
  background: #3b82f6;
  color: white;
  border-bottom-right-radius: 4px;
}

.friend-message .message-content {
  background: #f3f4f6;
  color: #111827;
  border-bottom-left-radius: 4px;
}

.message-content p {
  margin: 0;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message-meta {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
  margin-top: 4px;
  font-size: 11px;
  opacity: 0.7;
}

.friend-message .message-meta {
  justify-content: flex-start;
}

.read-status.read {
  color: #10b981;
}
</style>
