/**
 * Hook for managing speech synthesis (TTS) and speech recognition (STT)
 * Integrates Web Speech API with mood-based pitch/rate adjustments
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { Mood } from '../components/Avatar/emotions';

declare global {
  interface Window {
    webkitSpeechRecognition?: any;
    SpeechRecognition?: any;
  }
}

const SpeechRecognition =
  typeof window !== 'undefined'
    ? window.SpeechRecognition || window.webkitSpeechRecognition
    : null;
const SpeechSynthesis = typeof window !== 'undefined' ? window.speechSynthesis : null;

interface UseVoiceOptions {
  onTranscript?: (text: string) => void;
}

export function useVoice(options: UseVoiceOptions = {}) {
  const { onTranscript } = options;

  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [availableVoices, setAvailableVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoiceIndex, setSelectedVoiceIndex] = useState(0);

  const recognitionRef = useRef<any>(null);
  const lastSpokenTextRef = useRef<string>('');

  /**
   * Load available voices and filter to English
   */
  useEffect(() => {
    if (!SpeechSynthesis) return;

    const loadVoices = () => {
      const voices = SpeechSynthesis.getVoices();
      const englishVoices = voices.filter((voice: SpeechSynthesisVoice) =>
        voice.lang.startsWith('en')
      );
      setAvailableVoices(englishVoices);
      if (englishVoices.length > 0 && selectedVoiceIndex >= englishVoices.length) {
        setSelectedVoiceIndex(0);
      }
    };

    // Load voices immediately (cached)
    loadVoices();

    // Also listen for voice list updates
    SpeechSynthesis.onvoiceschanged = loadVoices;

    return () => {
      SpeechSynthesis.onvoiceschanged = null;
    };
  }, []);

  /**
   * Mood-based pitch and rate configuration
   */
  const getMoodSettings = (mood?: Mood) => {
    const settings = {
      pitch: 1.0,
      rate: 0.95,
    };

    if (!mood) return settings;

    switch (mood) {
      case 'excited':
        settings.pitch = 1.3;
        settings.rate = 1.1;
        break;
      case 'sad':
        settings.pitch = 0.8;
        settings.rate = 0.95;
        break;
      case 'happy':
        settings.pitch = 1.1;
        settings.rate = 0.95;
        break;
      case 'thinking':
        settings.pitch = 1.0;
        settings.rate = 0.85;
        break;
      case 'confused':
        settings.pitch = 1.05;
        settings.rate = 0.9;
        break;
      case 'neutral':
      default:
        settings.pitch = 1.0;
        settings.rate = 0.95;
    }

    return settings;
  };

  /**
   * Speak text with mood-based adjustments
   */
  const speak = useCallback(
    (text: string, mood?: Mood): Promise<void> => {
      return new Promise((resolve) => {
        if (!SpeechSynthesis) {
          console.error('Speech Synthesis not supported');
          resolve();
          return;
        }

        // Cancel any ongoing speech
        SpeechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        const settings = getMoodSettings(mood);

        utterance.pitch = settings.pitch;
        utterance.rate = settings.rate;
        utterance.volume = 1;

        // Set voice if available
        if (availableVoices.length > 0) {
          utterance.voice = availableVoices[selectedVoiceIndex] || availableVoices[0];
        }

        utterance.onstart = () => {
          setIsSpeaking(true);
        };

        utterance.onend = () => {
          setIsSpeaking(false);
          resolve();
        };

        utterance.onerror = (event) => {
          console.error('Speech synthesis error:', event.error);
          setIsSpeaking(false);
          resolve();
        };

        lastSpokenTextRef.current = text;
        SpeechSynthesis.speak(utterance);
      });
    },
    [availableVoices, selectedVoiceIndex]
  );

  /**
   * Start listening with Web Speech API
   */
  const startListening = useCallback(() => {
    if (!SpeechRecognition) {
      console.error('Speech Recognition not supported');
      return;
    }

    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }

    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;

    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    let interimTranscript = '';

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event: any) => {
      interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;

        if (event.results[i].isFinal) {
          // Final result
          if (onTranscript) {
            onTranscript(transcript);
          }
        } else {
          // Interim result
          interimTranscript += transcript;
        }
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  }, [onTranscript]);

  /**
   * Stop listening
   */
  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  }, []);

  /**
   * Replay last spoken text
   */
  const replayLastSpoken = useCallback(() => {
    if (lastSpokenTextRef.current) {
      speak(lastSpokenTextRef.current);
    }
  }, [speak]);

  return {
    // Methods
    speak,
    startListening,
    stopListening,
    replayLastSpoken,

    // State
    isListening,
    isSpeaking,
    availableVoices,
    selectedVoiceIndex,
    setSelectedVoiceIndex,
  };
}

export default useVoice;
