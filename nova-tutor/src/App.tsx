/**
 * Main App component - integrates Avatar, Chat, Voice controls with curriculum
 */

import React, { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import Avatar from './components/Avatar/Avatar';
import ChatPanel from './components/Chat/ChatPanel';
import VoiceControls from './components/Voice/VoiceControls';
import { get } from './api/client';
import {
  APP_LANGUAGE_STORAGE_KEY,
  AppLanguage,
  getInitialLanguage,
  resolveAppLanguage,
} from './i18n/config';
import { useCharacter } from './hooks/useCharacter';
import { useChat } from './hooks/useChat';
import { useVoice } from './hooks/useVoice';
import { Mood } from './types';
import './index.css';

interface SessionApiResponse {
  topic?: string;
  level?: string;
  language?: string;
  correct_answers?: number;
  total_attempts?: number;
}

const TOPIC_OPTIONS = [
  { value: 'variables', labelKey: 'topics.variables' },
  { value: 'data_types', labelKey: 'topics.dataTypes' },
  { value: 'conditionals', labelKey: 'topics.conditionals' },
  { value: 'loops', labelKey: 'topics.loops' },
  { value: 'functions', labelKey: 'topics.functions' },
  { value: 'lists', labelKey: 'topics.lists' },
  { value: 'dicts', labelKey: 'topics.dictionaries' },
] as const;

const LEVEL_OPTIONS = [
  { value: 'beginner', labelKey: 'levels.beginner' },
  { value: 'intermediate', labelKey: 'levels.intermediate' },
  { value: 'advanced', labelKey: 'levels.advanced' },
] as const;

const LANGUAGE_OPTIONS: AppLanguage[] = ['en', 'zh-TW', 'vi'];

function generateSessionId(): string {
  return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

function App() {
  const { i18n, t } = useTranslation();

  const [sessionId] = useState(() => {
    const stored = sessionStorage.getItem('sessionId');
    return stored || generateSessionId();
  });
  const [selectedTopic, setSelectedTopic] = useState('variables');
  const [selectedLevel, setSelectedLevel] = useState('beginner');
  const [selectedLanguage, setSelectedLanguage] = useState<AppLanguage>(getInitialLanguage);

  const { character, setEmotion } = useCharacter('happy');
  const chat = useChat({
    sessionId,
    topic: selectedTopic,
    level: selectedLevel,
    language: selectedLanguage,
    characterName: 'Nova',
  });

  const sessionStatsRef = useRef({
    correctAnswers: 0,
    totalAttempts: 0,
  });
  const lastSpokenAssistantIdRef = useRef<string | null>(null);

  useEffect(() => {
    if (chat.currentMood) {
      setEmotion(chat.currentMood as any);
    }
  }, [chat.currentMood, setEmotion]);

  const handleTranscript = (text: string) => {
    if (text && !chat.isStreaming) {
      setEmotion('thinking');
      chat.sendMessage(text).then(() => {
        setEmotion(chat.currentMood as any);
      });
    }
  };

  const voiceHook = useVoice({
    onTranscript: handleTranscript,
    language: selectedLanguage,
  });
  const { speak } = voiceHook;

  useEffect(() => {
    void i18n.changeLanguage(selectedLanguage);
    window.localStorage.setItem(APP_LANGUAGE_STORAGE_KEY, selectedLanguage);
  }, [i18n, selectedLanguage]);

  useEffect(() => {
    if (chat.isStreaming) return;

    const lastAssistantMessage = [...chat.messages]
      .reverse()
      .find((message) => message.role === 'assistant' && message.content.trim());

    if (!lastAssistantMessage) return;
    if (lastAssistantMessage.id === lastSpokenAssistantIdRef.current) return;
    if (lastAssistantMessage.content.startsWith('Error:')) return;

    lastSpokenAssistantIdRef.current = lastAssistantMessage.id;
    void speak(lastAssistantMessage.content, chat.currentMood);
  }, [chat.messages, chat.isStreaming, chat.currentMood, speak]);

  useEffect(() => {
    const restoreSession = async () => {
      try {
        const sessionData = await get<SessionApiResponse>(`/api/session/${sessionId}`);
        if (sessionData) {
          setSelectedTopic(sessionData.topic || 'variables');
          setSelectedLevel(sessionData.level || 'beginner');
          if (sessionData.language) {
            setSelectedLanguage(resolveAppLanguage(sessionData.language));
          }
          sessionStatsRef.current = {
            correctAnswers: sessionData.correct_answers || 0,
            totalAttempts: sessionData.total_attempts || 0,
          };
        }
      } catch (error) {
        console.log('No existing session, starting fresh');
      }
    };

    sessionStorage.setItem('sessionId', sessionId);
    restoreSession();
  }, [sessionId]);

  const testEmotions: Mood[] = ['happy', 'excited', 'thinking', 'confused', 'sad', 'neutral'];

  return (
    <div className="flex flex-col h-screen bg-gradient-to-b from-blue-50 to-indigo-100">
      <header className="bg-white shadow-md p-4">
        <div className="flex flex-wrap justify-between items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">{t('header.title')}</h1>
            <p className="text-gray-600 text-sm">{t('header.subtitle')}</p>
          </div>

          <div className="flex items-start gap-4">
            <div className="text-left">
              <label className="block text-xs font-semibold text-gray-700 mb-2">
                {t('common.language')}
              </label>
              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value as AppLanguage)}
                disabled={chat.isStreaming}
                className="px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              >
                {LANGUAGE_OPTIONS.map((language) => (
                  <option key={language} value={language}>
                    {language === 'en'
                      ? t('common.english')
                      : language === 'zh-TW'
                        ? t('common.traditionalChinese')
                        : t('common.vietnamese')}
                  </option>
                ))}
              </select>
            </div>

            <div className="text-right text-sm">
              <p className="text-gray-600">{t('session.label')} {sessionId.slice(0, 8)}...</p>
              <p className="text-gray-600">
                {t('session.correct')} {sessionStatsRef.current.correctAnswers} / {sessionStatsRef.current.totalAttempts}
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 flex overflow-hidden gap-4 p-4">
        <div className="w-60 bg-white shadow-lg rounded-lg flex flex-col">
          <div className="flex-1 flex flex-col items-center justify-center py-6">
            <Avatar mood={character.emotion as any} />
            <div className="mt-4 text-center">
              <p className="text-sm font-semibold text-gray-600 capitalize">
                {t('controls.mood')} {t(`emotions.${character.emotion}`)}
              </p>
            </div>
          </div>

          <div className="px-4 py-3 border-t border-gray-200">
            <label className="block text-xs font-semibold text-gray-700 mb-2">
              {t('controls.topic')}
            </label>
            <select
              value={selectedTopic}
              onChange={(e) => setSelectedTopic(e.target.value)}
              disabled={chat.isStreaming}
              className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            >
              {TOPIC_OPTIONS.map((topic) => (
                <option key={topic.value} value={topic.value}>
                  {t(topic.labelKey)}
                </option>
              ))}
            </select>
          </div>

          <div className="px-4 py-3 border-t border-gray-200">
            <label className="block text-xs font-semibold text-gray-700 mb-2">
              {t('controls.level')}
            </label>
            <select
              value={selectedLevel}
              onChange={(e) => setSelectedLevel(e.target.value)}
              disabled={chat.isStreaming}
              className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            >
              {LEVEL_OPTIONS.map((level) => (
                <option key={level.value} value={level.value}>
                  {t(level.labelKey)}
                </option>
              ))}
            </select>
          </div>

          <div className="px-4 py-3 border-t border-gray-200">
            <p className="text-xs font-semibold text-gray-700 mb-2">{t('controls.testEmotions')}</p>
            <div className="grid grid-cols-3 gap-1">
              {testEmotions.map((emotion) => (
                <button
                  key={emotion}
                  onClick={() => setEmotion(emotion)}
                  className="px-2 py-1 text-xs rounded bg-blue-100 hover:bg-blue-200 text-blue-700 capitalize"
                >
                  {t(`emotions.${emotion}`)}
                </button>
              ))}
            </div>
          </div>

          <div className="border-t border-gray-200">
            <VoiceControls voice={voiceHook} />
          </div>
        </div>

        <div className="flex-1 flex flex-col gap-4">
          <ChatPanel
            messages={chat.messages}
            isStreaming={chat.isStreaming}
            onSendMessage={chat.sendMessage}
            onStopStreaming={chat.stopStreaming}
          />

          {chat.error && (
            <div className="bg-red-50 border border-red-200 rounded p-3 text-sm text-red-700">
              <p>{chat.error}</p>
              <button
                onClick={chat.clearError}
                className="text-xs text-red-600 hover:text-red-800 mt-1"
              >
                {t('common.dismiss')}
              </button>
            </div>
          )}
        </div>
      </main>

      <footer className="bg-white border-t border-gray-200 px-6 py-3 text-center text-sm text-gray-600">
        <p>{chat.isStreaming ? t('footer.thinking') : t('footer.idle')}</p>
      </footer>
    </div>
  );
}

export default App;
