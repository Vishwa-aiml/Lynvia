import apiClient from '../client';
import type { Conversation, MessageListResponse, Message } from '../../types/chat';
import { auth } from '../../config/firebase';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const WS_BASE_URL = API_BASE_URL.replace(/^http/, 'ws');

export const chatService = {
  getConversation: (projectId: string) =>
    apiClient.get<Conversation>(`/projects/${projectId}/chat`),

  getMessages: (projectId: string, page = 1, limit = 50) =>
    apiClient.get<MessageListResponse>(`/projects/${projectId}/chat/messages`, {
      params: { page, limit },
    }),

  sendMessage: (projectId: string, data: { content: string, messageType: string }) =>
    apiClient.post<Message>(`/projects/${projectId}/chat/messages`, data),

  getUnreadCount: (projectId: string) =>
    apiClient.get<{ unreadCount: number }>(`/projects/${projectId}/chat/unread-count`),

  markAsRead: (projectId: string) =>
    apiClient.patch<{ updated: boolean }>(`/projects/${projectId}/chat/read`),
    
  createWebSocketConnection: async (projectId: string) => {
    const user = auth.currentUser;
    if (!user) return null;
    
    try {
      const token = await user.getIdToken();
      const wsUrl = `${WS_BASE_URL}/ws/projects/${projectId}/chat?token=${token}`;
      const ws = new WebSocket(wsUrl);
      return ws;
    } catch (e) {
      console.error("Failed to get auth token for websocket", e);
      return null;
    }
  }
};
