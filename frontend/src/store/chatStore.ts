/**
 * Chat Store - 重构版
 * 
 * 职责：
 * 1. 管理服务端会话 (sessionId)
 * 2. 管理 API 调用状态 (isLoading, error)
 * 3. 发送消息到后端 API
 * 
 * 注意：消息状态由 conversationStore 统一管理
 */
import { create } from 'zustand';
import { sendChatMessage, getSessionEvents } from '../api/agent';
import { getImageUrl } from '../api/storage';
import type { ChatMessage, ImageResult } from '../api/types';

// 消息回调类型
type MessageCallback = (message: ChatMessage) => void;

interface ChatStore {
    sessionId: string | null;
    isLoading: boolean;
    error: string | null;

    // 消息回调 - 当收到新消息时通知 conversationStore
    onNewMessage: MessageCallback | null;
    setOnNewMessage: (callback: MessageCallback | null) => void;

    // 核心方法
    sendMessage: (query: string, userMessage?: ChatMessage) => Promise<ChatMessage | null>;
    clearSession: () => void;
    setSessionId: (sessionId: string | null) => void;
}

export const useChatStore = create<ChatStore>((set, get) => ({
    sessionId: localStorage.getItem('chat_session_id'),
    isLoading: false,
    error: null,
    onNewMessage: null,

    setOnNewMessage: (callback) => set({ onNewMessage: callback }),

    sendMessage: async (query: string, userMessage?: ChatMessage): Promise<ChatMessage | null> => {
        const { sessionId, onNewMessage } = get();

        set({ isLoading: true, error: null });

        // Setup AbortController for timeout (120 seconds)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 120000);

        try {
            const response = await sendChatMessage({
                query,
                session_id: sessionId || undefined,
                top_k: 10,
            }, { signal: controller.signal });

            clearTimeout(timeoutId);

            if (!response || typeof response.session_id !== 'string' || typeof response.answer !== 'string') {
                throw new Error('服务器响应格式异常，请刷新页面后重试。');
            }

            // 更新 sessionId
            if (response.session_id && response.session_id !== sessionId) {
                localStorage.setItem('chat_session_id', response.session_id);
                set({ sessionId: response.session_id });
            }

            // 构建图片列表
            const images: ImageResult[] = response.results?.images?.map(img => ({
                ...img,
                preview_url: getImageUrl(img.id),
            })) || [];

            // 构建 agent 消息
            const agentMessage: ChatMessage = {
                id: crypto.randomUUID(),
                type: 'agent',
                content: response.answer,
                images: images.length > 0 ? images : undefined,
                suggestions: response.suggestions,
                timestamp: new Date(response.timestamp),
            };

            set({ isLoading: false });

            // 通知 conversationStore 保存消息
            if (onNewMessage) {
                onNewMessage(agentMessage);
            }

            return agentMessage;
        } catch (error: unknown) {
            clearTimeout(timeoutId);

            let errorMessage = error instanceof Error ? error.message : '发送失败';
            const errorRecord = typeof error === 'object' && error !== null ? (error as Record<string, unknown>) : null;
            const errorName = typeof errorRecord?.name === 'string' ? errorRecord.name : undefined;
            const errorCode = typeof errorRecord?.code === 'string' ? errorRecord.code : undefined;

            // Handle Timeout / Abort
            if (errorName === 'CanceledError' || errorName === 'AbortError' || errorCode === 'ERR_CANCELED') {
                errorMessage = '请求超时：检索可能较慢（首次加载/向量生成），请稍后重试。';
            }

            // 构建错误消息
            const errorMessageObj: ChatMessage = {
                id: crypto.randomUUID(),
                type: 'agent',
                content: `❌ ${errorMessage}`,
                timestamp: new Date(),
            };

            set({ isLoading: false, error: errorMessage });

            // 通知 conversationStore 保存错误消息
            if (onNewMessage) {
                onNewMessage(errorMessageObj);
            }

            return errorMessageObj;
        }
    },

    clearSession: () => {
        localStorage.removeItem('chat_session_id');
        set({ sessionId: null, error: null });
    },

    setSessionId: (sessionId) => {
        if (sessionId) {
            localStorage.setItem('chat_session_id', sessionId);
        } else {
            localStorage.removeItem('chat_session_id');
        }
        set({ sessionId });
    },
}));
