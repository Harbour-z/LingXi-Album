import { useState } from 'react';
import Lightbox from 'yet-another-react-lightbox';
import 'yet-another-react-lightbox/styles.css';
import type { ImageResult } from '../../api/types';

interface ImageLightboxProps {
    images: ImageResult[];
    currentIndex: number;
    isOpen: boolean;
    onClose: () => void;
}

export function ImageLightbox({ images, currentIndex, isOpen, onClose }: ImageLightboxProps) {
    const [index, setIndex] = useState(currentIndex);

    const slides = images.map(img => ({
        src: img.preview_url || `/api/v1/storage/images/${img.id}`,
        alt: img.metadata.filename,
        title: img.metadata.filename,
    }));

    return (
        <Lightbox
            open={isOpen}
            close={onClose}
            index={index}
            slides={slides}
            on={{ view: ({ index }) => setIndex(index) }}
            styles={{
                container: { backgroundColor: 'rgba(0, 0, 0, 0.9)' },
            }}
        />
    );
}
