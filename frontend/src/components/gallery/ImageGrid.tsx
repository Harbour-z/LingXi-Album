import { motion } from 'framer-motion';
import Masonry from 'react-masonry-css';
import { ImageCard } from './ImageCard';
import { EmptyState } from '../common/EmptyState';
import type { ImageResult } from '../../api/types';

interface ImageGridProps {
    images: ImageResult[];
    onImageClick?: (image: ImageResult, index: number) => void;
}

const breakpointColumns = {
    default: 4,
    1280: 3,
    1024: 3,
    768: 2,
    640: 2,
};

export function ImageGrid({ images, onImageClick }: ImageGridProps) {
    if (images.length === 0) {
        return <EmptyState />;
    }

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
        >
            <Masonry
                breakpointCols={breakpointColumns}
                className="flex gap-4 -ml-4"
                columnClassName="pl-4 bg-clip-padding"
            >
                {images.map((image, index) => (
                    <div key={image.id} className="mb-4">
                        <ImageCard
                            image={image}
                            onClick={() => onImageClick?.(image, index)}
                        />
                    </div>
                ))}
            </Masonry>
        </motion.div>
    );
}
