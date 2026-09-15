import React, { useState, useEffect, useRef } from 'react';
import { chatService } from '../../api/services/chat.service';
import type { Message } from '../../types/chat';
import { useAuth } from '../../context/AuthContext';
import { Send, Loader2, Paperclip } from 'lucide-react';

interface ChatTabProps {
  projectId: string;
}

export default function ChatTab({ projectId }: ChatTabProps) {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    fetchMessages();
    setupWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [projectId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchMessages = async () => {
    try {
      setIsLoading(true);
      // Ensure conversation exists
      await chatService.getConversation(projectId);
      const res = await chatService.getMessages(projectId, 1, 100);
      setMessages(res.data.messages.reverse()); // Reverse because backend usually sends newest first on paginated
    } catch (err) {
      console.error("Failed to fetch messages", err);
    } finally {
      setIsLoading(false);
    }
  };

  const setupWebSocket = async () => {
    const ws = await chatService.createWebSocketConnection(projectId);
    if (!ws) return;
    
    wsRef.current = ws;

    ws.onmessage = (event: MessageEvent) => {
      // In a real implementation, the backend would broadcast new messages here.
      // For MVP, if we receive a ping/message, we just refetch or parse it.
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'NEW_MESSAGE') {
          setMessages(prev => [...prev, data.message]);
        }
      } catch (e) {
        console.log("WS message:", event.data);
      }
    };
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    try {
      setIsSending(true);
      const res = await chatService.sendMessage(projectId, {
        content: newMessage,
        messageType: 'TEXT'
      });
      // Optimistic add
      setMessages(prev => [...prev, res.data]);
      setNewMessage('');
    } catch (err) {
      console.error("Failed to send message", err);
    } finally {
      setIsSending(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="animate-spin h-8 w-8 text-accent" />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[600px] bg-[#15151A] rounded-2xl border border-[#2A2A32] overflow-hidden">
      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-[#9A9AA3]">
            <p>No messages yet. Say hello!</p>
          </div>
        ) : (
          messages.map((msg) => {
            const isMine = msg.senderId === user?.id;
            const isSystem = msg.messageType === 'SYSTEM' || msg.messageType === 'MILESTONE_UPDATE';

            if (isSystem) {
              return (
                <div key={msg.id} className="flex justify-center my-4">
                  <span className="bg-[#2A2A32] text-[#9A9AA3] text-xs px-3 py-1 rounded-full">
                    {msg.content}
                  </span>
                </div>
              );
            }

            return (
              <div key={msg.id} className={`flex ${isMine ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[70%] rounded-2xl px-5 py-3 ${
                  isMine ? 'bg-accent text-white rounded-br-none' : 'bg-[#2A2A32] text-[#F5F5F5] rounded-bl-none'
                }`}>
                  <p className="text-sm">{msg.content}</p>
                  <span className={`text-[10px] mt-1 block ${isMine ? 'text-white/70 text-right' : 'text-[#9A9AA3]'}`}>
                    {new Date(msg.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <div className="p-4 bg-[#0D0D0F] border-t border-[#2A2A32]">
        <form onSubmit={handleSendMessage} className="flex items-center gap-2">
          <button type="button" className="p-3 text-[#9A9AA3] hover:text-[#F5F5F5] transition-colors rounded-xl hover:bg-[#2A2A32]">
            <Paperclip className="h-5 w-5" />
          </button>
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 bg-[#15151A] border border-[#2A2A32] rounded-xl px-4 py-3 text-[#F5F5F5] placeholder-[#9A9AA3]/50 focus:outline-none focus:border-accent"
          />
          <button
            type="submit"
            disabled={!newMessage.trim() || isSending}
            className="p-3 bg-accent text-white rounded-xl hover:bg-accent/90 transition-colors disabled:opacity-50"
          >
            {isSending ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
          </button>
        </form>
      </div>
    </div>
  );
}
