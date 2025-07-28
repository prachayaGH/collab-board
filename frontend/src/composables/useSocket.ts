import { ref, reactive } from "vue";
import { io } from "socket.io-client";
import { useAuthStore } from "@/stores/auth";
import type { Conversation, FriendRequest, Message, User } from "@/types";

export const useSocket = () => {
  const socket = ref<any>(null);
  const connected = ref(false);
  const authStore = useAuthStore();

  const messages = reactive<Record<string, Message[]>>({});
  const friends = ref<User[]>([]);
  const conversations = ref<Conversation[]>([]);
  const pendingRequests = ref<FriendRequest[]>([]);
  const sentRequests = ref<FriendRequest[]>([]);

  const connect = () => {
    const accessToken = document.cookie
      .split("; ")
      .find((row) => row.startsWith("access_token="))
      ?.split("=")[1];

    if (!accessToken) {
      console.error("No access token found");
      return;
    }

    console.log("Socket before emit:", socket.value);

    socket.value = io(import.meta.env.VITE_API_URL || "http://localhost:8000", {
      auth: {
        access_token: accessToken,
      },
      transports: ["websocket"],
    });

    // Connection events
    socket.value.on("connect", () => {
      connected.value = true;
      console.log("Connected to server");
    });

    socket.value.on("disconnect", () => {
      connected.value = false;
      console.log("Disconnected from server");
    });

    socket.value.on('error', (error: any) => {
      console.error('Socket error:', error)
    })

    // Friend events
    socket.value.on("friend_request_received", (data: any) => {
      pendingRequests.value.push(data);
      // Show notification
      showNotification(
        "New Friend Request",
        `${data.requester.display_name} sent you a friend request`
      );
    });

    socket.value.on("friend_request_responded", (data: any) => {
      if (data.action === "accept") {
        friends.value.push(data.user);
        showNotification(
          "Friend Request Accepted",
          `${data.user.display_name} accepted your friend request`
        );
      }
      // Remove from sent requests
      sentRequests.value = sentRequests.value.filter((req) => req.id !== data.id);
    });

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
    }
  };

  // Friend methods
  const sendFriendRequest = (email: string) => {
    if (socket.value) {
      socket.value.emit("send_friend_request", { email });
    }
    console.log(`Friend request sent to ${email}`);
  };

  const respondToFriendRequest = (requestId: number, action: "accept" | "decline") => {
    if (socket.value) {
      socket.value.emit("respond_friend_request", {
        request_id: requestId,
        action,
      });
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
    const convIndex = conversations.value.findIndex((conv) => conv.friend.id === friendId);

    if (convIndex >= 0) {
      conversations.value[convIndex].last_message = message;
      if (message.sender_id !== authStore.user?.id && !message.is_read) {
        conversations.value[convIndex].unread_count++;
      }
      // Move to top
      const conv = conversations.value.splice(convIndex, 1)[0];
      conversations.value.unshift(conv);
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
    sendFriendRequest,
    respondToFriendRequest,
    joinChat,
    sendMessage,
    markMessagesRead,
    getChatMessages,
  };
};
