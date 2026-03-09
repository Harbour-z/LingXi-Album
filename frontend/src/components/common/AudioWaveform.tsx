import React, { useEffect, useRef, useCallback } from 'react';

interface AudioWaveformProps {
  isRecording: boolean;
  audioLevel?: number;
  color?: string;
  backgroundColor?: string;
  height?: number;
  barCount?: number;
  barWidth?: number;
  barGap?: number;
}

export const AudioWaveform: React.FC<AudioWaveformProps> = ({
  isRecording,
  audioLevel = 0,
  color = '#1677ff',
  backgroundColor = 'transparent',
  height = 40,
  barCount = 32,
  barWidth = 3,
  barGap = 2,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);
  const barsRef = useRef<number[]>([]);
  const targetBarsRef = useRef<number[]>([]);

  const initBars = useCallback(() => {
    barsRef.current = Array(barCount).fill(0);
    targetBarsRef.current = Array(barCount).fill(0);
  }, [barCount]);

  useEffect(() => {
    initBars();
  }, [initBars]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const width = (barWidth + barGap) * barCount - barGap;
    
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.scale(dpr, dpr);

    const draw = () => {
      ctx.clearRect(0, 0, width, height);
      ctx.fillStyle = backgroundColor;
      ctx.fillRect(0, 0, width, height);

      const centerY = height / 2;
      const maxHeight = height * 0.8;

      for (let i = 0; i < barCount; i++) {
        if (isRecording) {
          const noise = Math.random() * 0.3;
          const baseLevel = audioLevel * (0.5 + Math.sin(i * 0.5) * 0.3);
          targetBarsRef.current[i] = Math.max(0.1, baseLevel + noise);
        } else {
          targetBarsRef.current[i] = 0;
        }

        barsRef.current[i] += (targetBarsRef.current[i] - barsRef.current[i]) * 0.15;

        const barHeight = barsRef.current[i] * maxHeight;
        const x = i * (barWidth + barGap);
        
        const gradient = ctx.createLinearGradient(0, centerY - barHeight / 2, 0, centerY + barHeight / 2);
        gradient.addColorStop(0, color);
        gradient.addColorStop(0.5, color);
        gradient.addColorStop(1, `${color}80`);

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.roundRect(x, centerY - barHeight / 2, barWidth, barHeight, barWidth / 2);
        ctx.fill();
      }

      animationRef.current = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isRecording, audioLevel, color, backgroundColor, height, barCount, barWidth, barGap]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    />
  );
};

export default AudioWaveform;