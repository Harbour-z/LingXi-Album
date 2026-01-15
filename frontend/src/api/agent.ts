import client from './client';
import type { ChatRequest, ChatResponse } from './types';

export async function sendChatMessage(params: ChatRequest): Promise<ChatResponse> {
    const { data } = await client.post('/agent/chat', params);
    return data;
}

export async function createSession(userId?: string): Promise<string> {
    const { data } = await client.post('/agent/session/create', null, {
        params: { user_id: userId }
    });
    return data.session_id;
}
