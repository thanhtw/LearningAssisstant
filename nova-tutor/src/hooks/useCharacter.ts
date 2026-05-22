/**
 * Hook for managing character emotion state and animations
 */

import { useState, useCallback } from 'react';
import { Emotion, Character } from '../types';

export function useCharacter(initialEmotion: Emotion = 'neutral') {
  const [character, setCharacter] = useState<Character>({
    emotion: initialEmotion,
    isAnimating: false,
    expression: '',
  });

  const setEmotion = useCallback((emotion: Emotion) => {
    setCharacter((prev) => ({
      ...prev,
      emotion,
      isAnimating: true,
    }));

    // Stop animation after it completes
    const timer = setTimeout(() => {
      setCharacter((prev) => ({
        ...prev,
        isAnimating: false,
      }));
    }, 600);

    return () => clearTimeout(timer);
  }, []);

  const setExpression = useCallback((expression: string) => {
    setCharacter((prev) => ({
      ...prev,
      expression,
    }));
  }, []);

  const animateEmotion = useCallback((emotion: Emotion, duration = 3000) => {
    setEmotion(emotion);

    const timer = setTimeout(() => {
      setCharacter((prev) => ({
        ...prev,
        emotion: initialEmotion,
        isAnimating: true,
      }));
    }, duration);

    return () => clearTimeout(timer);
  }, [setEmotion, initialEmotion]);

  return {
    character,
    setEmotion,
    setExpression,
    animateEmotion,
  };
}

export default useCharacter;
