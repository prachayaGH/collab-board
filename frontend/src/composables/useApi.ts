import api from '@/utils/auth'


export const useApi = () => {
  // Friends API
  const getFriends = async () => {
    const { data } = await api.get('/friends/')
    return data
  }

  const getPendingRequests = async () => {
    const { data } = await api.get('/friends/requests/pending')
    return data
  }

  const getSentRequests = async () => {
    const { data } = await api.get('/friends/requests/sent')
    return data
  }

  const searchUsers = async (query: string) => {
    const { data } = await api.get(`/friends/search?q=${encodeURIComponent(query)}`)
    return data
  }

  const sendFriendRequest = async (email: string) => {
    const { data } = await api.post('/friends/request', { email })
    console.log(`Friend request sent to ${email}:`, data)
    return data
  }

  const respondToFriendRequest = async (requestId: number, action: 'accept' | 'decline') => {
    const { data } = await api.post('/friends/respond', {
      request_id: requestId,
      action
    })
    return data
  }

  // Chat API
  const getChatHistory = async (friendId: number, limit = 50) => {
    const { data } = await api.get(`/chat/history/${friendId}?limit=${limit}`)
    return data
  }

  const getConversations = async () => {
    const { data } = await api.get('/chat/conversations')
    return data
  }

  const sendMessage = async (receiverId: number, content: string) => {
    const { data } = await api.post('/chat/send', {
      receiver_id: receiverId,
      content
    })
    return data
  }

  const markMessagesRead = async (senderId: number) => {
    const { data } = await api.post(`/chat/read/${senderId}`)
    return data
  }

  const getUnreadCount = async () => {
    const { data } = await api.get('/chat/unread-count')
    return data
  }

  // Notifications API
  const getNotifications = async () => {
    const { data } = await api.get('/notifications/')
    return data
  }

  const markNotificationRead = async (notificationId: number) => {
    const { data } = await api.post(`/notifications/${notificationId}/read`)
    return data
  }

  const getUnreadNotificationCount = async () => {
    const { data } = await api.get('/notifications/unread-count')
    return data
  }

  return {
    // Friends
    getFriends,
    getPendingRequests,
    getSentRequests,
    searchUsers,
    sendFriendRequest,
    respondToFriendRequest,
    // Chat
    getChatHistory,
    getConversations,
    sendMessage,
    markMessagesRead,
    getUnreadCount,
    // Notifications
    getNotifications,
    markNotificationRead,
    getUnreadNotificationCount
  }
}

