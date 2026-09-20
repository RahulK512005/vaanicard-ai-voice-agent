import React from 'react';
import { Volume2, User, Bot, Sparkles } from 'lucide-react';
import { ChatMessage as ChatMessageType } from '../types/conversation';

interface ChatMessageProps {
  message: ChatMessageType;
  onReplayAudio?: (text: string) => void;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, onReplayAudio }) => {
  const isUser = message.sender === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'} my-2`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-amber-500 to-orange-600 flex items-center justify-center text-white shrink-0 shadow-md">
          <Bot className="w-4 h-4" />
        </div>
      )}

      <div
        className={`max-w-lg rounded-2xl p-4 shadow-sm ${
          isUser
            ? 'bg-amber-600 text-white rounded-br-none'
            : 'bg-gray-800/90 text-gray-100 border border-gray-700/60 rounded-bl-none'
        }`}
      >
        <div className="flex items-center justify-between gap-3 mb-1">
          <span className="text-[11px] font-semibold tracking-wider uppercase opacity-75 flex items-center gap-1">
            {isUser ? (
              <>
                <User className="w-3 h-3" /> You {message.isVoiceInput && '(Spoken)'}
              </>
            ) : (
              <>
                <Sparkles className="w-3 h-3 text-amber-400" /> VaaniCart Assistant
              </>
            )}
          </span>

          {!isUser && message.spokenOutput && onReplayAudio && (
            <button
              onClick={() => onReplayAudio(message.spokenOutput!.text)}
              className="text-gray-400 hover:text-amber-400 transition-colors p-1 rounded hover:bg-gray-700/50 cursor-pointer"
              title="Replay spoken audio"
            >
              <Volume2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        <p className="text-sm sm:text-base leading-relaxed whitespace-pre-wrap">{message.text}</p>
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-gray-200 shrink-0">
          <User className="w-4 h-4" />
        </div>
      )}
    </div>
  );
};
