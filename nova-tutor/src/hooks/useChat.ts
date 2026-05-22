/**
 * Hook for managing chat with streaming responses and mood updates
 */

import { useState, useCallback, useRef } from 'react';
import { Message, ChatState, Mood } from '../types';
import { streamChat } from '../api/client';

export interface UseChatParams {
  sessionId: string;
  topic: string;
  level?: string;
  characterName?: string;
}

export function useChat(params: UseChatParams) {
  const [state, setState] = useState<ChatState>({
    messages: [],
    isStreaming: false,
    error: null,
    currentMood: 'happy',
  });

  const messageIdRef = useRef(0);
  const abortStreamRef = useRef<(() => void) | null>(null);
  const partialMessageIdRef = useRef<string | null>(null);

  const addMessage = useCallback((content: string, role: 'user' | 'assistant') => {
    const newMessage: Message = {
      id: `msg-${messageIdRef.current++}`,
      content,
      role,
      timestamp: new Date(),
    };

    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, newMessage],
    }));

    return newMessage;
  }, []);

  const updateLastMessage = useCallback((content: string) => {
    setState((prev) => {
      if (prev.messages.length === 0) return prev;
      const lastMsg = prev.messages[prev.messages.length - 1];
      if (lastMsg.role !== 'assistant') return prev;
      
      return {
        ...prev,
        messages: [
          ...prev.messages.slice(0, -1),
          { ...lastMsg, content },
        ],
      };
    });
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return;

      // Add user message
      addMessage(content, 'user');

      // Initialize streaming state
      setState((prev) => ({
        ...prev,
        isStreaming: true,
        error: null,
      }));

      // Create placeholder for assistant response
      const placeholderId = `msg-${messageIdRef.current}`;
      messageIdRef.current++;
      partialMessageIdRef.current = placeholderId;
      
      setState((prev) => ({
        ...prev,
        messages: [
          ...prev.messages,
          {
            id: placeholderId,
            content: '',
            role: 'assistant',
            timestamp: new Date(),
          },
        ],
      }));

      let accumulatedText = '';

      // Abort any previous stream
      if (abortStreamRef.current) {
        abortStreamRef.current();
      }

      // Start streaming
      abortStreamRef.current = streamChat({
        sessionId: params.sessionId,
        message: content,
        topic: params.topic,
        level: params.level || 'beginner',
        characterName: params.characterName || 'Nova',
        
        onToken: (text: string) => {
          accumulatedText += text;
          updateLastMessage(accumulatedText);
        },
        
        onMood: (mood: Mood) => {
          setState((prev) => ({
            ...prev,
            currentMood: mood,
          }));
        },
        
        onDone: (fullText: string) => {
          // Ensure we have the complete text
          updateLastMessage(fullText || accumulatedText);
          setState((prev) => ({
            ...prev,
            isStreaming: false,
          }));
          abortStreamRef.current = null;
        },
        
        onError: (error: string) => {
          setState((prev) => ({
            ...prev,
            isStreaming: false,
            error,
          }));
          addMessage(`Error: ${error}`, 'assistant');
          abortStreamRef.current = null;
        },
      });
    },
    [params.sessionId, params.topic, params.level, params.characterName, addMessage, updateLastMessage]
  );

  const clearHistory = useCallback(() => {
    // Abort any streaming
    if (abortStreamRef.current) {
      abortStreamRef.current();
      abortStreamRef.current = null;
    }

    setState({
      messages: [],
      isStreaming: false,
      error: null,
      currentMood: 'happy',
    });
    messageIdRef.current = 0;
    partialMessageIdRef.current = null;
  }, []);

  const clearError = useCallback(() => {
    setState((prev) => ({
      ...prev,
      error: null,
    }));
  }, []);

  const stopStreaming = useCallback(() => {
    if (abortStreamRef.current) {
      abortStreamRef.current();
      abortStreamRef.current = null;
    }
    setState((prev) => ({
      ...prev,
      isStreaming: false,
    }));
  }, []);

  return {
    ...state,
    addMessage,
    sendMessage,
    clearHistory,
    clearError,
    stopStreaming,
  };
}

export default useChat;
