export interface User {
  id: number
  display_name: string
  avatar_url: string | null
  email: string
  status?: 'online' | 'offline'
  last_seen?: string
  relationship: "none" | "requested" | "friends" | "incoming"
}

export interface Message {
  id: number
  sender_id: number
  receiver_id: number
  content: string
  is_read: boolean
  created_at: string
  sender: User
}

export interface Conversation {
  friend: User
  last_message: Message | null
  unread_count: number
}

export interface FriendRequest {
  id: number
  requester: User
  addressee: User
  created_at: string
}
