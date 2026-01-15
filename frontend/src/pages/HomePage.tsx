import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Camera, Search, Mic } from 'lucide-react';
import { useState } from 'react';
import { useChatStore } from '../store/chatStore';

const suggestions = [
    { icon: '🌅', text: '日落时的海滩' },
    { icon: '🐕', text: '可爱的小狗' },
    { icon: '🏔️', text: '山间风景' },
    { icon: '🎂', text: '生日聚会' },
    { icon: '🌸', text: '春天的花' },
];

export function HomePage() {
    const navigate = useNavigate();
    const { sendMessage, isLoading } = useChatStore();
    const [query, setQuery] = useState('');

    const handleSearch = async (text: string) => {
        if (!text.trim()) return;
        await sendMessage(text);
        navigate('/chat');
    };

    return (
        <div className="min-h-screen bg-[#fafafa]">
            {/* Header */}
            <header className="flex items-center justify-between px-6 py-4">
                <div className="flex items-center gap-2">
                    <Camera className="text-indigo-600" size={24} />
                    <span className="text-gray-800 font-medium">智慧相册</span>
                </div>
                <div className="flex items-center gap-3">
                    <button className="px-5 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors">
                        登录
                    </button>
                    <button className="px-5 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                        注册
                    </button>
                </div>
            </header>

            {/* Main content */}
            <main className="flex flex-col items-center px-6 pt-32">
                {/* Title */}
                <motion.h1
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4 }}
                    className="text-3xl font-semibold text-gray-800 mb-10"
                >
                    我能为你做些什么？
                </motion.h1>

                {/* Search Card */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: 0.1 }}
                    className="w-full max-w-[680px] mb-8"
                >
                    <div className="bg-[#f4f4f5] rounded-2xl overflow-hidden">
                        {/* Input area */}
                        <div className="px-5 pt-5 pb-3">
                            <input
                                type="text"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSearch(query)}
                                placeholder="有什么我能帮您的吗？"
                                className="w-full bg-transparent text-gray-800 placeholder-gray-400 outline-none text-base"
                            />
                        </div>
                        
                        {/* Toolbar */}
                        <div className="flex items-center justify-between px-4 py-3">
                            <div className="flex items-center gap-2">
                                <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-200 rounded-lg transition-colors">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <line x1="12" y1="5" x2="12" y2="19"></line>
                                        <line x1="5" y1="12" x2="19" y2="12"></line>
                                    </svg>
                                </button>
                                <button className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-200 rounded-lg transition-colors">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <circle cx="12" cy="12" r="10"></circle>
                                        <path d="M12 6v6l4 2"></path>
                                    </svg>
                                    <span>深度思考</span>
                                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <path d="M6 9l6 6 6-6"></path>
                                    </svg>
                                </button>
                                <button className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-200 rounded-lg transition-colors">
                                    <Search size={16} />
                                    <span>搜索</span>
                                </button>
                            </div>
                            <button
                                onClick={() => handleSearch(query)}
                                disabled={!query.trim() || isLoading}
                                className="w-9 h-9 flex items-center justify-center rounded-full bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                            >
                                {isLoading ? (
                                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                ) : (
                                    <Mic size={18} />
                                )}
                            </button>
                        </div>
                    </div>
                </motion.div>

                {/* Suggestion chips */}
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: 0.2 }}
                    className="flex flex-wrap justify-center gap-3"
                >
                    {suggestions.map((item, index) => (
                        <button
                            key={index}
                            onClick={() => handleSearch(item.text)}
                            className="flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-gray-200 text-gray-600 text-sm hover:border-gray-300 hover:shadow-sm transition-all"
                        >
                            <span>{item.icon}</span>
                            <span>{item.text}</span>
                        </button>
                    ))}
                </motion.div>
            </main>

            {/* Footer */}
            <footer className="fixed bottom-0 left-0 right-0 py-4 text-center text-xs text-gray-400">
                使用智慧相册，即表示您同意我们的 <span className="text-indigo-500 cursor-pointer hover:underline">用户条款</span> 和 <span className="text-indigo-500 cursor-pointer hover:underline">隐私协议</span>
            </footer>
        </div>
    );
}
