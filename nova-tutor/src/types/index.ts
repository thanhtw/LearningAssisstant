/**
 * Shared TypeScript types for the Nova Tutor application
 */

export type Emotion = 'happy' | 'sad' | 'excited' | 'confused' | 'neutral' | 'thinking';
export type Mood = Emotion; // Alias for consistency

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

export interface ChatState {
  messages: Message[];
  isStreaming: boolean;
  error: string | null;
  currentMood: Mood;
}

export interface Character {
  emotion: Emotion;
  isAnimating: boolean;
  expression: string;
}

export interface VoiceState {
  isListening: boolean;
  isSpeaking: boolean;
  transcript: string;
  error: string | null;
}

export interface SessionInfo {
  sessionId: string;
  topic: string;
  level: string;
  characterName: string;
  correctAnswers: number;
  totalAttempts: number;
  mood: Mood;
}
