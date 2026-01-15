import { useState } from 'react';
import { Send } from 'lucide-react';

interface InputBarProps {
    onSend: (message: string) => void;
    isLoading?: boolean;
    placeholder?: string;
}

export function InputBar({
    onSend,
    isLoading = false,
    placeholder = '描述你想找的图片...'
}: InputBarProps) {
    const [input, setInput] = useState('');

    const handleSubmit = () => {
        if (input.trim() && !isLoading) {
            onSend(input.trim());
            setInput('');
        }
    };

    return (
        <div className="bg-[#f4f4f5] rounded-2xl">
            <div className="px-5 pt-4 pb-3">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
                    placeholder={placeholder}
                    disabled={isLoading}
                    className="w-full bg-transparent text-gray-800 placeholder-gray-400 outline-none text-base"
                />
            </div>
            <div className="flex items-center justify-between px-4 py-3">
                <div className="flex items-center gap-1">
                    <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-200 rounded-lg transition-colors">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="12" y1="5" x2="12" y2="19"></line>
                            <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                    </button>
                </div>
                <button
                    onClick={handleSubmit}
                    disabled={!input.trim() || isLoading}
                    className="w-9 h-9 flex items-center justify-center rounded-full bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                    {isLoading ? (
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ) : (
                        <Send size={16} />
                    )}
                </button>
            </div>
        </div>
    );
}
