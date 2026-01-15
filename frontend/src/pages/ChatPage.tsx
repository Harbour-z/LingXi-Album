import { Link } from 'react-router-dom';
import { ArrowLeft, Trash2, Camera } from 'lucide-react';
import { ChatContainer } from '../components/chat/ChatContainer';
import { useChatStore } from '../store/chatStore';

export function ChatPage() {
    const { clearHistory, messages } = useChatStore();

    return (
        <div className="min-h-screen bg-[#fafafa] flex flex-col">
            {/* Header */}
            <header className="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-100">
                <Link
                    to="/"
                    className="flex items-center gap-2 text-gray-500 hover:text-indigo-600 transition-colors"
                >
                    <ArrowLeft size={18} />
                    <span className="text-sm">返回</span>
                </Link>

                <div className="flex items-center gap-2">
                    <Camera className="text-indigo-600" size={20} />
                    <span className="text-gray-800 font-medium">智慧相册</span>
                </div>

                {messages.length > 0 ? (
                    <button
                        onClick={clearHistory}
                        className="flex items-center gap-1.5 text-gray-400 hover:text-red-500 transition-colors text-sm"
                    >
                        <Trash2 size={16} />
                        <span>清空</span>
                    </button>
                ) : (
                    <div className="w-16" />
                )}
            </header>

            {/* Chat area */}
            <main className="flex-1 overflow-hidden">
                <ChatContainer />
            </main>
        </div>
    );
}
