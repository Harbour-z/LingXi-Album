import { useEffect, useRef } from 'react';

interface PerformanceMetrics {
  componentName: string;
  renderCount: number;
  lastRenderTime: number;
  averageRenderTime: number;
  maxRenderTime: number;
}

const performanceCache = new Map<string, PerformanceMetrics>();

export function usePerformanceMonitor(componentName: string, enabled: boolean = process.env.NODE_ENV === 'development') {
  const renderCountRef = useRef(0);
  const renderTimesRef = useRef<number[]>([]);
  const mountTimeRef = useRef<number>(Date.now());

  useEffect(() => {
    if (!enabled) return;

    renderCountRef.current++;
    const renderTime = Date.now() - mountTimeRef.current;
    renderTimesRef.current.push(renderTime);

    if (renderTimesRef.current.length > 10) {
      renderTimesRef.current.shift();
    }

    const metrics: PerformanceMetrics = {
      componentName,
      renderCount: renderCountRef.current,
      lastRenderTime: renderTime,
      averageRenderTime: renderTimesRef.current.reduce((a, b) => a + b, 0) / renderTimesRef.current.length,
      maxRenderTime: Math.max(...renderTimesRef.current),
    };

    performanceCache.set(componentName, metrics);

    if (renderTime > 16) {
      console.warn(`[Performance] ${componentName} slow render detected: ${renderTime}ms`);
    }

    mountTimeRef.current = Date.now();
  });

  useEffect(() => {
    return () => {
      if (!enabled) return;

      const metrics = performanceCache.get(componentName);
      if (metrics) {
        console.log(`[Performance] ${componentName} unmounted:`, {
          totalRenders: metrics.renderCount,
          avgRenderTime: `${metrics.averageRenderTime.toFixed(2)}ms`,
          maxRenderTime: `${metrics.maxRenderTime.toFixed(2)}ms`,
        });
      }
    };
  }, [componentName, enabled]);

  return {
    getMetrics: () => performanceCache.get(componentName),
    getAllMetrics: () => Array.from(performanceCache.values()),
  };
}
