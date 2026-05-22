/**
 * Emotion configuration map for Avatar animations and styling
 */

export type Mood = 'happy' | 'sad' | 'excited' | 'confused' | 'neutral' | 'thinking';

export type EmotionConfig = {
  name: string;
  color: string;
  scale: number;
  animationDuration: number; // in milliseconds
  mouthPath: string;
  eyeRy: number;
  cheekOpacity: number;
  browYOffset: number; // vertical offset for eyebrows
  browRotation: number; // rotation angle in degrees
};

export const emotionMap: Record<Mood, EmotionConfig> = {
  happy: {
    name: 'Happy',
    color: '#FFD93D',
    scale: 1.1,
    animationDuration: 300,
    mouthPath: 'M 45 70 Q 60 80 75 70',
    eyeRy: 8,
    cheekOpacity: 0.4,
    browYOffset: -3,
    browRotation: -10,
  },
  sad: {
    name: 'Sad',
    color: '#6C5CE7',
    scale: 0.9,
    animationDuration: 400,
    mouthPath: 'M 45 75 Q 60 65 75 75',
    eyeRy: 6,
    cheekOpacity: 0.1,
    browYOffset: 5,
    browRotation: 15,
  },
  excited: {
    name: 'Excited',
    color: '#FF6B6B',
    scale: 1.15,
    animationDuration: 250,
    mouthPath: 'M 42 68 Q 60 85 78 68',
    eyeRy: 10,
    cheekOpacity: 0.6,
    browYOffset: -8,
    browRotation: -20,
  },
  confused: {
    name: 'Confused',
    color: '#FFA502',
    scale: 1.0,
    animationDuration: 500,
    mouthPath: 'M 45 72 L 75 72',
    eyeRy: 7,
    cheekOpacity: 0.2,
    browYOffset: 0,
    browRotation: 5,
  },
  neutral: {
    name: 'Neutral',
    color: '#74B9FF',
    scale: 1.0,
    animationDuration: 350,
    mouthPath: 'M 45 72 L 75 72',
    eyeRy: 7,
    cheekOpacity: 0.15,
    browYOffset: 0,
    browRotation: 0,
  },
  thinking: {
    name: 'Thinking',
    color: '#A29BFE',
    scale: 1.05,
    animationDuration: 600,
    mouthPath: 'M 45 73 Q 60 70 75 73',
    eyeRy: 6,
    cheekOpacity: 0.25,
    browYOffset: 3,
    browRotation: 10,
  },
};

export function getMoodConfig(mood: Mood): EmotionConfig {
  return emotionMap[mood];
}

// For backward compatibility
export function getEmotionConfig(emotion: string): EmotionConfig {
  return emotionMap[emotion as Mood] || emotionMap.neutral;
}
