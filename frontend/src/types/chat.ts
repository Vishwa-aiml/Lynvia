export interface Conversation {
  id: string;
  projectId: string;
  lastMessageAt: string | null;
  createdAt: string;
}

export interface Message {
  id: string;
  conversationId: string;
  senderId: string | null; // null for SYSTEM messages
  content: string;
  messageType: 'TEXT' | 'FILE' | 'SYSTEM' | 'MILESTONE_UPDATE';
  replyToMessageId: string | null;
  isDeleted: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface MessageListResponse {
  messages: Message[];
  total: number;
  page: number;
  limit: number;
  hasNext: boolean;
}
