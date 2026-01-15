import { motion } from 'framer-motion';
import { User, Bot } from 'lucide-react';
import { ImageGrid } from '../gallery/ImageGrid';
import type { ChatMessage, ImageResult } from '../../api/types';

interface MessageBubbleProps {
    message: ChatMessage;
    onImageClick?: (image: ImageResult, index: number) => void;
    onSuggestionClick?: (suggestion: string) => void;
}

export function MessageBubble({ message, onImageClick, onSuggestionClick }: MessageBubbleProps) {
    const isUser = message.type === 'user';

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className={`flex items-start gap-4 ${isUser ? 'flex-row-reverse' : ''}`}
        >
            {/* Avatar */}
            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                isUser ? 'bg-indigo-600' : 'bg-indigo-600'
            }`}>
                {isUser ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
            </div>

            {/* Content */}
            <div className={`flex-1 max-w-[80%] ${isUser ? 'flex flex-col items-end' : ''}`}>
                <div className={`rounded-2xl px-5 py-4 ${
                    isUser
                        ? 'bg-indigo-600 text-white'
                        : 'bg-white text-gray-800 shadow-sm'
                }`}>
                    <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{message.content}</p>
                </div>

                {/* Images */}
                {message.images && message.images.length > 0 && (
                    <div className="mt-5 w-full">
                        <ImageGrid images={message.images} onImageClick={onImageClick} />
                    </div>
                )}

                {/* Suggestions */}
                {message.suggestions && message.suggestions.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-4">
                        {message.suggestions.map((suggestion, i) => (
                            <button
                                key={i}
                                onClick={() => onSuggestionClick?.(suggestion)}
                                className="text-sm px-4 py-2 rounded-full bg-white border border-gray-200 text-gray-600 hover:border-indigo-300 hover:text-indigo-600 transition-colors"
                            >
                                {suggestion}
                            </button>
                        ))}
                    </div>
                )}

                {/* Timestamp */}
                <p className="text-xs text-gray-400 mt-3">
                    {message.timestamp.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
                </p>
            </div>
        </motion.div>
    );
}
