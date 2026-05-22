/**
 * Individual message bubble component for chat display
 */

import React from 'react';
import { Message } from '../../types';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`message-bubble-container ${isUser ? 'user' : 'assistant'}`}>
      <div className={`message-bubble ${isUser ? 'bg-blue-500' : 'bg-gray-300'}`}>
        <p className={isUser ? 'text-white' : 'text-gray-900'}>{message.content}</p>
        <span className={`message-time text-xs ${isUser ? 'text-blue-100' : 'text-gray-600'}`}>
          {message.timestamp.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
      </div>
    </div>
  );
};

export default MessageBubble;
