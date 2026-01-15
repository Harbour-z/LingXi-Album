import { useRef, useEffect, useState } from 'react';
import { MessageBubble } from './MessageBubble';
import { InputBar } from './InputBar';
import { ImageLightbox } from '../gallery/ImageLightbox';
import { useChatStore } from '../../store/chatStore';
import type { ImageResult } from '../../api/types';

export function ChatContainer() {
    const { messages, isLoading, sendMessage } = useChatStore();
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const [lightboxOpen, setLightboxOpen] = useState(false);
    const [lightboxImages, setLightboxImages] = useState<ImageResult[]>([]);
    const [lightboxIndex, setLightboxIndex] = useState(0);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleImageClick = (images: ImageResult[], image: ImageResult, index: number) => {
        setLightboxImages(images);
        setLightboxIndex(index);
        setLightboxOpen(true);
    };

    const handleSuggestionClick = (suggestion: string) => {
        sendMessage(suggestion);
    };

    return (
        <div className="flex flex-col h-full bg-[#fafafa]">
            {/* Messages area */}
            <div className="flex-1 overflow-y-auto px-6 py-8">
                <div className="max-w-3xl mx-auto space-y-8">
                    {messages.length === 0 && (
                        <div className="flex flex-col items-center justify-center py-24 text-gray-400">
                            <p className="text-lg font-medium">开始搜索你的图片吧</p>
                            <p className="text-sm mt-3">试试 "海边的日落" 或 "上周的聚会照片"</p>
                        </div>
                    )}

                    {messages.map((message) => (
                        <MessageBubble
                            key={message.id}
                            message={message}
                            onImageClick={(img, idx) => message.images && handleImageClick(message.images, img, idx)}
                            onSuggestionClick={handleSuggestionClick}
                        />
                    ))}

                    {isLoading && (
                        <div className="flex items-start gap-4">
                            <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center flex-shrink-0">
                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            </div>
                            <div className="bg-white rounded-2xl px-5 py-4 shadow-sm">
                                <p className="text-sm text-gray-500">正在搜索...</p>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input area */}
            <div className="p-4 bg-white border-t border-gray-100">
                <div className="max-w-3xl mx-auto">
                    <InputBar onSend={sendMessage} isLoading={isLoading} />
                </div>
            </div>

            {/* Lightbox */}
            <ImageLightbox
                images={lightboxImages}
                currentIndex={lightboxIndex}
                isOpen={lightboxOpen}
                onClose={() => setLightboxOpen(false)}
            />
        </div>
    );
}
