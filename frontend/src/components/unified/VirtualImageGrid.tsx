import React, { useMemo, useCallback, useState, useRef, useEffect } from 'react';
import { Image, Empty, Spin, Tag } from 'antd';
import { motion, AnimatePresence } from 'framer-motion';
import type { ImageResult } from '../../api/types';

interface VirtualImageGridProps {
  images: ImageResult[];
  loading?: boolean;
  onImageClick?: (image: ImageResult) => void;
  itemHeight?: number;
  containerHeight?: number;
}

const IMAGE_VARIANTS = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.8 },
};

export const VirtualImageGrid: React.FC<VirtualImageGridProps> = ({
  images,
  loading = false,
  onImageClick,
  itemHeight = 300,
  containerHeight = 600,
}) => {
  const [visibleRange, setVisibleRange] = useState({ start: 0, end: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  const columns = useMemo(() => {
    const containerWidth = containerRef.current?.clientWidth || 1200;
    const minWidth = 280;
    const gap = 16;
    const calculated = Math.floor((containerWidth - gap) / (minWidth + gap));
    return Math.max(2, Math.min(6, calculated));
  }, [containerRef.current?.clientWidth]);

  const rows = useMemo(() => Math.ceil(images.length / columns), [images.length, columns]);

  const totalHeight = rows * itemHeight;

  const updateVisibleRange = useCallback(() => {
    if (!containerRef.current) return;

    const scrollTop = containerRef.current.scrollTop;
    const containerHeight = containerRef.current.clientHeight;
    const buffer = itemHeight * 2;

    const startRow = Math.max(0, Math.floor((scrollTop - buffer) / itemHeight));
    const endRow = Math.min(rows, Math.ceil((scrollTop + containerHeight + buffer) / itemHeight));

    setVisibleRange({
      start: startRow * columns,
      end: Math.min(endRow * columns, images.length),
    });
  }, [rows, columns, itemHeight, images.length]);

  useEffect(() => {
    updateVisibleRange();
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      requestAnimationFrame(updateVisibleRange);
    };

    container.addEventListener('scroll', handleScroll, { passive: true });
    window.addEventListener('resize', updateVisibleRange, { passive: true });

    return () => {
      container.removeEventListener('scroll', handleScroll);
      window.removeEventListener('resize', updateVisibleRange);
    };
  }, [updateVisibleRange]);

  const getImageStyle = useCallback((index: number) => {
    const row = Math.floor(index / columns);
    return {
      position: 'absolute' as const,
      top: row * itemHeight,
      left: (index % columns) * (100 / columns) + '%',
      width: `calc(${100 / columns}% - 16px)`,
      height: itemHeight - 8,
    };
  }, [columns, itemHeight]);

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: containerHeight,
      }}>
        <Spin size="large" />
      </div>
    );
  }

  if (images.length === 0) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: containerHeight,
      }}>
        <Empty description="暂无搜索结果" />
      </div>
    );
  }

  const visibleImages = images.slice(visibleRange.start, visibleRange.end);

  return (
    <div
      ref={containerRef}
      style={{
        height: containerHeight,
        overflowY: 'auto',
        position: 'relative',
      }}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <AnimatePresence mode="popLayout">
          {visibleImages.map((image, index) => {
            const actualIndex = visibleRange.start + index;
            return (
              <motion.div
                key={image.id}
                variants={IMAGE_VARIANTS}
                initial="hidden"
                animate="visible"
                exit="exit"
                transition={{ duration: 0.3, delay: (actualIndex % columns) * 0.05 }}
                style={getImageStyle(actualIndex)}
                onClick={() => onImageClick?.(image)}
                whileHover={{ scale: 1.02, boxShadow: '0 8px 25px rgba(0,0,0,0.15)' }}
                whileTap={{ scale: 0.98 }}
              >
                <div style={{
                  width: '100%',
                  height: '100%',
                  borderRadius: 12,
                  overflow: 'hidden',
                  cursor: 'pointer',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                }}>
                  <div style={{ width: '100%', height: 'calc(100% - 40px)', overflow: 'hidden' }}>
                    <Image
                      src={`/api/v1/storage/images/${image.id}`}
                      alt={image.metadata.description || image.id}
                      loading="lazy"
                      style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover',
                      }}
                      preview={false}
                    />
                  </div>
                  <div style={{
                    padding: '8px 12px',
                    background: 'rgba(255,255,255,0.95)',
                    backdropFilter: 'blur(8px)',
                  }}>
                    <div style={{
                      fontSize: 12,
                      color: '#666',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      marginBottom: 4,
                    }}>
                      {image.metadata.description || '暂无描述'}
                    </div>
                    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                      {image.metadata.tags.slice(0, 2).map((tag, i) => (
                        <Tag key={i} style={{ margin: 0, fontSize: 11 }}>
                          {tag}
                        </Tag>
                      ))}
                      {image.metadata.tags.length > 2 && (
                        <Tag style={{ margin: 0, fontSize: 11 }}>
                          +{image.metadata.tags.length - 2}
                        </Tag>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
};
