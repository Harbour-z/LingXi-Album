import { create } from 'zustand';
import { sendChatMessage } from '../api/agent';
import { getImageUrl } from '../api/storage';
import type { ChatMessage, ImageResult } from '../api/types';

interface ChatStore {
    sessionId: string | null;
    messages: ChatMessage[];
    isLoading: boolean;
    error: string | null;
    sendMessage: (query: string, topK?: number) => Promise<void>;
    clearHistory: () => void;
}

export const useChatStore = create<ChatStore>((set, get) => ({
    sessionId: localStorage.getItem('chat_session_id'),
    messages: [],
    isLoading: false,
    error: null,

    sendMessage: async (query: string, topK: number = 10) => {
        const { sessionId, messages } = get();

        const userMessage: ChatMessage = {
            id: crypto.randomUUID(),
            type: 'user',
            content: query,
            timestamp: new Date(),
        };

        set({ messages: [...messages, userMessage], isLoading: true, error: null });

        try {
            const response = await sendChatMessage({
                query,
                session_id: sessionId || undefined,
                top_k: topK,
            });

            if (response.session_id && response.session_id !== sessionId) {
                localStorage.setItem('chat_session_id', response.session_id);
                set({ sessionId: response.session_id });
            }

            const images: ImageResult[] = response.results?.images?.map(img => ({
                ...img,
                preview_url: getImageUrl(img.id),
            })) || [];

            const agentMessage: ChatMessage = {
                id: crypto.randomUUID(),
                type: 'agent',
                content: response.answer,
                images: images.length > 0 ? images : undefined,
                suggestions: response.suggestions,
                timestamp: new Date(response.timestamp),
            };

            set(state => ({
                messages: [...state.messages, agentMessage],
                isLoading: false,
            }));
        } catch (error) {
            set({
                isLoading: false,
                error: error instanceof Error ? error.message : '发送失败'
            });
        }
    },

    clearHistory: () => {
        localStorage.removeItem('chat_session_id');
        set({ sessionId: null, messages: [], error: null });
    },
}));
