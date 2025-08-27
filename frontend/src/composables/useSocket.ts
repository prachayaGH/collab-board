import { ref, reactive } from "vue";
import { io } from "socket.io-client";
import type { Conversation, FriendRequest, Message, User } from "@/types";
import { useAuthStore } from "@/stores/auth";

  const socket = ref<any>(null);
  const connected = ref(false);

  const messages = reactive<Record<string, Message[]>>({});
  const friends = ref<User[]>([]);
  const conversations = ref<Conversation[]>([]);
  const pendingRequests = ref<FriendRequest[]>([]);
  const sentRequests = ref<FriendRequest[]>([]);

  let initialized = false;

export const useSocket = () => {
  const authStore = useAuthStore();

  const connect = () => {
    if (initialized) return; // ป้องกัน connect ซ้ำ
    initialized = true;

    socket.value = io(import.meta.env.VITE_API_URL || "http://localhost:8000", {
    path: "/socket.io/",
    transports: ["websocket"],
    withCredentials: true
  });

    // Connection events
    socket.value.on("connect", () => {
      connected.value = true;
      console.log("✅ Connected to server with id:", socket.value.id);
    });

    socket.value.on("disconnect", () => {
      connected.value = false;
      console.log("❌ Disconnected from server");
    });

    socket.value.on('error', (error: any) => {
      console.error('Socket error:', error)
    })

    socket.value.on("friend_status_changed", (data: any) => {
      const friend = friends.value.find((f) => f.id === parseInt(data.user_id));
      if (friend) {
        friend.status = data.status;
      }
    });

    // Chat events
    socket.value.on("message_received", (message: Message) => {
      const chatKey = getChatKey(message.sender_id, message.receiver_id);
      if (!messages[chatKey]) {
        messages[chatKey] = [];
      }
      messages[chatKey].push(message);

      // Update conversation
      updateConversation(message);
    });

    socket.value.on("new_message_notification", (data: any) => {
      showNotification(`New message from ${data.sender.display_name}`, data.message.content);
    });

    socket.value.on("messages_marked_read", (data: any) => {
      const chatKey = getChatKey(data.sender_id, data.receiver_id);
      if (messages[chatKey]) {
        messages[chatKey].forEach((msg) => {
          if (msg.sender_id === data.sender_id) {
            msg.is_read = true;
          }
        });
      }
    });
  };

  const disconnect = () => {
    if (socket.value) {
      socket.value.disconnect();
      socket.value = null;
      connected.value = false;
      initialized = false;
    }
  };

  // Chat methods
  const joinChat = (friendId: number) => {
    if (socket.value) {
      socket.value.emit("join_chat", { friend_id: friendId });
    }
  };

  const sendMessage = (receiverId: number, content: string) => {
    if (socket.value) {
      socket.value.emit("send_message", {
        receiver_id: receiverId,
        content,
      });
    }
  };

  const markMessagesRead = (senderId: number) => {
    if (socket.value) {
      socket.value.emit("mark_messages_read", { sender_id: senderId });
    }

    // reset unread count
    const conv = conversations.value.find((c) => c.friend.id === senderId);
    if (conv) conv.unread_count = 0;
  };

  // Helper functions
  const getChatKey = (userId1: number, userId2: number): string => {
    return `${Math.min(userId1, userId2)}_${Math.max(userId1, userId2)}`;
  };

  const getChatMessages = (friendId: number): Message[] => {
    const currentUserId = authStore.user?.id;
    if (!currentUserId) return [];

    const chatKey = getChatKey(currentUserId, friendId);
    return messages[chatKey] || [];
  };

  const updateConversation = (message: Message) => {
    const friendId =
      message.sender_id === authStore.user?.id ? message.receiver_id : message.sender_id;

    let conv = conversations.value.find((c) => c.friend.id === friendId);

    if (!conv) {
      // ถ้าไม่มี conversation ให้สร้างใหม่
      conv = {
        friend: { 
          id: friendId, 
          display_name: "Unknown", 
          avatar_url: "", 
          email: "", // placeholder email
          relationship: "none" // default relationship
        }, // placeholder
        last_message: message,
        unread_count: 0,
      };
      conversations.value.unshift(conv);
    } else {
      conv.last_message = message;
    }

    // เพิ่ม unread ถ้าเพื่อนได้ส่งมา
    if (message.sender_id !== authStore.user?.id && !message.is_read) {
      conv.unread_count = (conv.unread_count || 0) + 1;
    }

    // เลื่อน conv ไปบนสุด
    const idx = conversations.value.findIndex((c) => c.friend.id === friendId);
    if (idx > 0) {
      const [moved] = conversations.value.splice(idx, 1);
      conversations.value.unshift(moved);
    }
  };


  const showNotification = (title: string, body: string) => {
    if ("Notification" in window && Notification.permission === "granted") {
      new Notification(title, { body });
    }
  };

  return {
    get socket() { return socket.value },
    connected,
    messages,
    friends,
    conversations,
    pendingRequests,
    sentRequests,
    connect,
    disconnect,
    joinChat,
    sendMessage,
    markMessagesRead,
    getChatMessages,
  };
};
