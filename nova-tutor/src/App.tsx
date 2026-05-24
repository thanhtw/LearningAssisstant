/**
 * Main App component - integrates Avatar, Chat, Voice controls with curriculum
 */

import React, { useState, useEffect, useRef } from 'react';
import Avatar from './components/Avatar/Avatar';
import ChatPanel from './components/Chat/ChatPanel';
import VoiceControls from './components/Voice/VoiceControls';
import { useCharacter } from './hooks/useCharacter';
import { useChat } from './hooks/useChat';
import { useVoice } from './hooks/useVoice';
import { Mood } from './types';
import { get } from './api/client';
import './index.css';

interface SessionApiResponse {
  topic?: string;
  level?: string;
  correct_answers?: number;
  total_attempts?: number;
}

function generateSessionId(): string {
  return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

function App() {
  // Session state
  const [sessionId] = useState(() => {
    const stored = sessionStorage.getItem('sessionId');
    return stored || generateSessionId();
  });

  const [selectedTopic, setSelectedTopic] = useState('variables');
  const [selectedLevel, setSelectedLevel] = useState('beginner');

  // Character and chat state
  const { character, setEmotion } = useCharacter('happy');
  const chat = useChat({
    sessionId,
    topic: selectedTopic,
    level: selectedLevel,
    characterName: 'Nova',
  });

  const sessionStatsRef = useRef({
    correctAnswers: 0,
    totalAttempts: 0,
  });
  const lastSpokenAssistantIdRef = useRef<string | null>(null);

  // Sync current mood to avatar
  useEffect(() => {
    if (chat.currentMood) {
      setEmotion(chat.currentMood as any);
    }
  }, [chat.currentMood, setEmotion]);

  // Voice integration
  const handleTranscript = (text: string) => {
    if (text && !chat.isStreaming) {
      setEmotion('thinking');
      chat.sendMessage(text).then(() => {
        setEmotion(chat.currentMood as any);
      });
    }
  };

  const voiceHook = useVoice({ onTranscript: handleTranscript });
  const { speak } = voiceHook;

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

  // Fetch session state on mount
  useEffect(() => {
    const restoreSession = async () => {
      try {
        const sessionData = await get<SessionApiResponse>(`/api/session/${sessionId}`);
        if (sessionData) {
          setSelectedTopic(sessionData.topic || 'variables');
          setSelectedLevel(sessionData.level || 'beginner');
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

  // Emotions for quick testing
  const testEmotions: Mood[] = ['happy', 'excited', 'thinking', 'confused', 'sad', 'neutral'];

  return (
    <div className="flex flex-col h-screen bg-gradient-to-b from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-md p-4">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Nova Tutor</h1>
            <p className="text-gray-600 text-sm">Your AI Learning Assistant</p>
          </div>
          <div className="text-right text-sm">
            <p className="text-gray-600">Session: {sessionId.slice(0, 8)}...</p>
            <p className="text-gray-600">
              Correct: {sessionStatsRef.current.correctAnswers} / {sessionStatsRef.current.totalAttempts}
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden gap-4 p-4">
        {/* Left Panel - Avatar & Controls (240px) */}
        <div className="w-60 bg-white shadow-lg rounded-lg flex flex-col">
          {/* Avatar Display */}
          <div className="flex-1 flex flex-col items-center justify-center py-6">
            <Avatar mood={character.emotion as any} />
            <div className="mt-4 text-center">
              <p className="text-sm font-semibold text-gray-600 capitalize">
                Mood: {character.emotion}
              </p>
            </div>
          </div>

          {/* Topic Selector */}
          <div className="px-4 py-3 border-t border-gray-200">
            <label className="block text-xs font-semibold text-gray-700 mb-2">
              Topic
            </label>
            <select
              value={selectedTopic}
              onChange={(e) => setSelectedTopic(e.target.value)}
              disabled={chat.isStreaming}
              className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            >
              <option value="variables">Variables</option>
              <option value="data_types">Data Types</option>
              <option value="conditionals">Conditionals</option>
              <option value="loops">Loops</option>
              <option value="functions">Functions</option>
              <option value="lists">Lists</option>
              <option value="dicts">Dictionaries</option>
            </select>
          </div>

          {/* Level Selector */}
          <div className="px-4 py-3 border-t border-gray-200">
            <label className="block text-xs font-semibold text-gray-700 mb-2">
              Level
            </label>
            <select
              value={selectedLevel}
              onChange={(e) => setSelectedLevel(e.target.value)}
              disabled={chat.isStreaming}
              className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>

          {/* Emotion Buttons */}
          <div className="px-4 py-3 border-t border-gray-200">
            <p className="text-xs font-semibold text-gray-700 mb-2">Test Emotions</p>
            <div className="grid grid-cols-3 gap-1">
              {testEmotions.map((emotion) => (
                <button
                  key={emotion}
                  onClick={() => setEmotion(emotion)}
                  className="px-2 py-1 text-xs rounded bg-blue-100 hover:bg-blue-200 text-blue-700 capitalize"
                >
                  {emotion}
                </button>
              ))}
            </div>
          </div>

          {/* Voice Controls */}
          <div className="border-t border-gray-200">
            <VoiceControls voice={voiceHook} />
          </div>
        </div>

        {/* Right Panel - Chat & Stats */}
        <div className="flex-1 flex flex-col gap-4">
          {/* Chat Panel */}
          <ChatPanel
            messages={chat.messages}
            isStreaming={chat.isStreaming}
            onSendMessage={chat.sendMessage}
            onStopStreaming={chat.stopStreaming}
          />
          
          {/* Error Display */}
          {chat.error && (
            <div className="bg-red-50 border border-red-200 rounded p-3 text-sm text-red-700">
              <p>{chat.error}</p>
              <button
                onClick={chat.clearError}
                className="text-xs text-red-600 hover:text-red-800 mt-1"
              >
                Dismiss
              </button>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 px-6 py-3 text-center text-sm text-gray-600">
        <p>
          {chat.isStreaming
            ? 'Nova is thinking...'
            : 'Ask questions or use voice commands to learn'}
        </p>
      </footer>
    </div>
  );
}

export default App;
