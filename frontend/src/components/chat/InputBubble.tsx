import React, { useState, useEffect } from 'react';
import { Card } from 'antd';
import './InputBubble.scss';

interface InputBubbleProps {
  children: React.ReactNode;
  className?: string;
  isTyping?: boolean;
  onTypingChange?: (isTyping: boolean) => void;
}

export const InputBubble: React.FC<InputBubbleProps> = ({
  children,
  className,
  isTyping = false,
  onTypingChange,
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [colorVariant, setColorVariant] = useState(() => {
    const colors = ['blue', 'purple', 'pink', 'cyan', 'green', 'orange'];
    return colors[Math.floor(Math.random() * colors.length)];
  });

  useEffect(() => {
    const detectTheme = () => {
      const isDark = document.documentElement.classList.contains('dark') ||
                     window.matchMedia('(prefers-color-scheme: dark)').matches;
      setTheme(isDark ? 'dark' : 'light');
    };

    detectTheme();

    const observer = new MutationObserver(detectTheme);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class'],
    });

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', detectTheme);

    return () => {
      observer.disconnect();
      window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', detectTheme);
    };
  }, []);

  useEffect(() => {
    if (onTypingChange) {
      onTypingChange(isTyping);
    }
  }, [isTyping, onTypingChange]);

  const handleFocus = () => {
    setIsFocused(true);
    const colors = ['blue', 'purple', 'pink', 'cyan', 'green', 'orange'];
    setColorVariant(colors[Math.floor(Math.random() * colors.length)]);
  };

  const handleBlur = () => {
    setIsFocused(false);
  };

  const bubbleClassName = `input-bubble ${theme}-theme color-${colorVariant} ${isTyping ? 'is-typing' : ''} ${className || ''}`;

  return (
    <Card
      className={bubbleClassName}
      onFocus={handleFocus}
      onBlur={handleBlur}
      tabIndex={0}
    >
      <div className="input-content">
        {children}
      </div>
    </Card>
  );
};
