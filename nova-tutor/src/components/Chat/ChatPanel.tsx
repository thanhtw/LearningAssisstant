/**
 * Chat panel component with message list and input
 */

import React, { useRef, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Message } from '../../types';
import MessageBubble from './MessageBubble';
import { SendMessageOverrides } from '../../hooks/useChat';

interface TopicOption {
  value: string;
  label: string;
}

interface ChatPanelProps {
  messages: Message[];
  isStreaming?: boolean;
  selectedTopic: string;
  selectedTopicLabel: string;
  selectedLevelLabel: string;
  topicOptions: TopicOption[];
  onTopicSelect: (topic: string) => void;
  onSendMessage: (content: string, overrides?: SendMessageOverrides) => void;
  onStopStreaming?: () => void;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({
  messages,
  isStreaming = false,
  selectedTopic,
  selectedTopicLabel,
  selectedLevelLabel,
  topicOptions,
  onTopicSelect,
  onSendMessage,
  onStopStreaming,
}) => {
  const { t } = useTranslation();
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSendMessage(inputValue);
      setInputValue('');
    }
  };

  const handleSuggestionClick = (topic: TopicOption) => {
    onTopicSelect(topic.value);
    onSendMessage(
      t('chat.suggestionExplainPrompt', { topic: topic.label }),
      { topic: topic.value }
    );
  };

  return (
    <div className="chat-panel flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Messages Container */}
      <div className="chat-messages flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="max-w-2xl w-full rounded-2xl border border-blue-100 bg-gradient-to-br from-blue-50 to-white p-6 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-wide text-blue-600">
                {t('chat.suggestionBadge')}
              </p>
              <h2 className="mt-2 text-2xl font-semibold text-slate-900">
                {t('chat.suggestionTitle')}
              </h2>
              <p className="mt-2 text-sm text-slate-600">
                {t('chat.suggestionSubtitle')}
              </p>

              <div className="mt-4 rounded-xl border border-slate-200 bg-white p-4">
                <p className="text-sm font-medium text-slate-700">
                  {t('chat.currentTopicLabel')} <span className="text-slate-900">{selectedTopicLabel}</span>
                </p>
                <p className="mt-1 text-sm text-slate-500">
                  {t('chat.currentLevelLabel')} {selectedLevelLabel}
                </p>
                <button
                  type="button"
                  onClick={() => handleSuggestionClick({ value: selectedTopic, label: selectedTopicLabel })}
                  disabled={isStreaming}
                  className="mt-4 inline-flex items-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
                >
                  {t('chat.explainSelectedTopic', { topic: selectedTopicLabel })}
                </button>
              </div>

              <div className="mt-5">
                <p className="text-sm font-medium text-slate-700">
                  {t('chat.otherTopicsLabel')}
                </p>
                <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                  {topicOptions.map((topic) => (
                    <button
                      key={topic.value}
                      type="button"
                      onClick={() => handleSuggestionClick(topic)}
                      disabled={isStreaming}
                      className={`rounded-xl border px-4 py-3 text-left transition ${
                        topic.value === selectedTopic
                          ? 'border-blue-300 bg-blue-50 text-blue-900'
                          : 'border-slate-200 bg-white text-slate-800 hover:border-blue-200 hover:bg-blue-50'
                      } disabled:cursor-not-allowed disabled:opacity-60`}
                    >
                      <span className="block text-sm font-semibold">{topic.label}</span>
                      <span className="mt-1 block text-xs text-slate-500">
                        {t('chat.topicCardHint')}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))
        )}
        {isStreaming && (
          <div className="message-bubble-container assistant">
            <div className="message-bubble bg-gray-300">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="chat-input-form p-4 border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={t('chat.placeholder')}
            disabled={isStreaming}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
          />
          <button
            type={isStreaming ? 'button' : 'submit'}
            onClick={isStreaming ? onStopStreaming : undefined}
            disabled={!isStreaming && !inputValue.trim()}
            className={`px-6 py-2 text-white rounded-lg transition-colors ${
              isStreaming
                ? 'bg-red-500 hover:bg-red-600'
                : 'bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400'
            }`}
          >
            {isStreaming ? t('chat.stop') : t('chat.send')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatPanel;
