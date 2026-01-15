import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import type { ImageResult } from '../../api/types';

interface ImageCardProps {
    image: ImageResult;
    onClick?: () => void;
}

export function ImageCard({ image, onClick }: ImageCardProps) {
    const [isLoaded, setIsLoaded] = useState(false);
    const [isInView, setIsInView] = useState(false);
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setIsInView(true);
                    observer.disconnect();
                }
            },
            { rootMargin: '100px' }
        );

        if (ref.current) observer.observe(ref.current);
        return () => observer.disconnect();
    }, []);

    const imageUrl = image.preview_url || `/api/v1/storage/images/${image.id}`;

    return (
        <motion.div
            ref={ref}
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            onClick={onClick}
            className="group relative overflow-hidden rounded-xl cursor-pointer bg-[#f4f4f5] hover:shadow-md transition-all"
        >
            <div className="aspect-square relative">
                {!isLoaded && (
                    <div className="absolute inset-0 bg-[#e4e4e7] animate-pulse" />
                )}
                {isInView && (
                    <img
                        src={imageUrl}
                        alt={image.metadata.filename}
                        onLoad={() => setIsLoaded(true)}
                        className={`w-full h-full object-cover transition-transform duration-300 group-hover:scale-105 ${
                            isLoaded ? 'opacity-100' : 'opacity-0'
                        }`}
                    />
                )}
            </div>

            {/* Hover overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                <div className="absolute bottom-0 left-0 right-0 p-3">
                    <p className="text-white text-sm font-medium truncate">
                        {image.metadata.filename}
                    </p>
                    <span className="inline-block mt-1 text-xs text-white/90 bg-indigo-600/90 px-2 py-0.5 rounded">
                        {Math.round(image.score * 100)}% 匹配
                    </span>
                </div>
            </div>
        </motion.div>
    );
}
