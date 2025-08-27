import api from '@/utils/auth'

export const useApi = () => {
  // Friends API
  const getFriends = async () => {
    try {
      const { data } = await api.get('/friends')
      return data
    } catch (error) {
      console.error("Error fetching friends:", error)
      throw error
    }
  }

  const getPendingRequests = async () => {
    try {
      const { data } = await api.get('/friends/requests/pending')
      return data
    } catch (error) {
      console.error("Error fetching pending requests:", error)
      throw error
    }
  }

  const getSentRequests = async () => {
    try {
      const { data } = await api.get('/friends/requests/sent')
      return data
    } catch (error) {
      console.error("Error fetching sent requests:", error)
      throw error
    }
  }

  const searchUsers = async (query: string) => {
    try {
      const { data } = await api.get(`/friends/search?q=${encodeURIComponent(query)}`)
      return data
    } catch (error) {
      console.error("Error searching users:", error)
      throw error
    }
  }

  const sendFriendRequest = async (email: string) => {
    try {
      const { data } = await api.post('/friends/request', { email })
      console.log(`Friend request sent to ${email}:`, data)
      return data
    } catch (error) {
      console.error("Friend request error:", error)
      throw error
    }
  }

  const respondToFriendRequest = async (requestId: number, action: 'accept' | 'decline') => {
    try {
      const { data } = await api.post('/friends/respond', {
        request_id: requestId,
        action
      })
      console.log(`Friend request ${action}:`, data)
      return data
    } catch (error) {
      console.error("Respond to friend request error:", error)
      throw error
    }
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

