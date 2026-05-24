/**
 * Voice controls component with microphone, speaker, voice selector, and speaking indicator
 */

import React, { useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import type { UseVoiceResult } from '../../hooks/useVoice';
import './VoiceControls.css';

interface VoiceControlsProps {
  voice: UseVoiceResult;
}

export const VoiceControls: React.FC<VoiceControlsProps> = ({
  voice,
}) => {
  const { t } = useTranslation();
  const {
    isListening,
    isSpeaking,
    hasSpokenText,
    hasMatchingVoice,
    availableVoices,
    selectedVoiceIndex,
    setSelectedVoiceIndex,
    startListening,
    stopListening,
    speak,
    replayLastSpoken,
  } = voice;

  const handleMicClick = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  const handleSpeakerClick = useCallback(() => {
    if (hasSpokenText) {
      replayLastSpoken();
      return;
    }

    void speak(t('voice.speakerTestMessage'));
  }, [hasSpokenText, replayLastSpoken, speak, t]);

  const handleVoiceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const index = parseInt(e.target.value, 10);
    setSelectedVoiceIndex(index);
  };

  return (
    <div className="voice-controls-container">
      {/* Microphone Button (STT) */}
      <button
        onClick={handleMicClick}
        className={`voice-button mic-button ${isListening ? 'active' : ''}`}
        title={isListening ? t('voice.stopListening') : t('voice.startListening')}
        disabled={isSpeaking}
        aria-label={isListening ? t('voice.stopListening') : t('voice.startListening')}
      >
        <svg
          className="w-6 h-6"
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          {isListening ? (
            <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z" />
          ) : (
            <path d="M12 1C6.48 1 2 5.48 2 11v6h2v-6c0-3.59 2.91-6.5 6.5-6.5s6.5 2.91 6.5 6.5v6h2v-6c0-5.52-4.48-10-10-10z" />
          )}
        </svg>
      </button>

      {/* Speaker Button (Replay) */}
      <button
        onClick={handleSpeakerClick}
        className={`voice-button speaker-button ${isSpeaking ? 'active' : ''}`}
        title={hasSpokenText ? t('voice.replayLastSpoken') : t('voice.testSpeaker')}
        disabled={isListening}
        aria-label={hasSpokenText ? t('voice.replayLastSpoken') : t('voice.testSpeaker')}
      >
        <svg
          className="w-6 h-6"
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.26 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z" />
        </svg>
      </button>

      {/* Voice Selector Dropdown */}
      {availableVoices.length > 0 && (
        <select
          value={selectedVoiceIndex}
          onChange={handleVoiceChange}
          className="voice-selector"
          title={t('voice.selectVoice')}
          disabled={isListening || isSpeaking}
        >
          {availableVoices.map((voice, index) => (
            <option key={index} value={index}>
              {voice.name} {voice.default ? t('voice.defaultVoiceSuffix') : ''}
            </option>
          ))}
        </select>
      )}

      {!hasMatchingVoice && (
        <p className="text-xs text-slate-500 text-center px-2">
          {t('voice.systemVoiceFallback')}
        </p>
      )}

      {/* Speaking Indicator */}
      <div className="voice-indicator">
        {isListening && (
          <span className="listening-indicator">
            <span className="listening-dot"></span>
            {t('voice.listeningIndicator')}
          </span>
        )}
        {isSpeaking && (
          <span className="speaking-indicator">
            <span className="speaking-dots">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </span>
            {t('voice.speakingIndicator')}
          </span>
        )}
        {!isListening && !isSpeaking && (
          <span className="idle-indicator">{t('voice.readyIndicator')}</span>
        )}
      </div>
    </div>
  );
};

export default VoiceControls;
