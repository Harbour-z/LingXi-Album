import { ImageOff } from 'lucide-react';

interface EmptyStateProps {
    title?: string;
    description?: string;
}

export function EmptyState({
    title = '暂无结果',
    description = '尝试使用其他关键词搜索'
}: EmptyStateProps) {
    return (
        <div className="flex flex-col items-center justify-center py-16 text-gray-400">
            <ImageOff size={48} className="mb-4 opacity-50" />
            <h3 className="text-lg font-medium">{title}</h3>
            <p className="text-sm mt-1">{description}</p>
        </div>
    );
}
