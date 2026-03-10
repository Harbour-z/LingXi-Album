import React, { useEffect, useState } from 'react';

interface TypewriterPart {
  text: string;
  style?: React.CSSProperties;
}

interface TypewriterEffectProps {
  parts: TypewriterPart[];
  speed?: number;
  cursorColor?: string;
}

export const TypewriterEffect: React.FC<TypewriterEffectProps> = ({
  parts,
  speed = 100,
  cursorColor = '#1677ff'
}) => {
  const [displayedParts, setDisplayedParts] = useState<TypewriterPart[]>([]);
  const [currentPartIndex, setCurrentPartIndex] = useState(0);
  const [currentCharIndex, setCurrentCharIndex] = useState(0);
  const [showCursor, setShowCursor] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => {
      setShowCursor(prev => !prev);
    }, 500);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (currentPartIndex >= parts.length) {
      return;
    }

    const timer = setTimeout(() => {
      const currentPart = parts[currentPartIndex];
      const nextCharIndex = currentCharIndex + 1;

      if (nextCharIndex <= currentPart.text.length) {
        setCurrentCharIndex(nextCharIndex);

        const newDisplayedParts = [...displayedParts];
        if (currentPartIndex >= newDisplayedParts.length) {
          newDisplayedParts.push({ text: '', style: currentPart.style });
        }
        newDisplayedParts[currentPartIndex] = {
          text: currentPart.text.substring(0, nextCharIndex),
          style: currentPart.style
        };
        setDisplayedParts(newDisplayedParts);
      } else {
        setCurrentPartIndex(prev => prev + 1);
        setCurrentCharIndex(0);
      }
    }, speed);

    return () => clearTimeout(timer);
  }, [currentPartIndex, currentCharIndex, parts, speed, displayedParts]);

  return (
    <span>
      {displayedParts.map((part, index) => (
        <span key={index} style={part.style}>
          {part.text}
        </span>
      ))}
      {currentPartIndex < parts.length && (
        <span
          style={{
            color: cursorColor,
            opacity: showCursor ? 1 : 0,
            marginLeft: 2,
            fontWeight: 'bold'
          }}
        >
          |
        </span>
      )}
    </span>
  );
};
