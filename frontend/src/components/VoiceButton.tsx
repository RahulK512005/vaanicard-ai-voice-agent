import React from 'react';
import { Mic, MicOff, Volume2, Square, Loader2, AlertCircle } from 'lucide-react';
import { VoiceState } from '../types/conversation';

interface VoiceButtonProps {
  state: VoiceState;
  onStartListening: () => void;
  onStopListening: () => void;
  onStopSpeaking: () => void;
}

export const VoiceButton: React.FC<VoiceButtonProps> = ({
  state,
  onStartListening,
  onStopListening,
  onStopSpeaking
}) => {
  const handleClick = () => {
    if (state === 'LISTENING') {
      onStopListening();
    } else if (state === 'SPEAKING') {
      onStopSpeaking();
    } else if (state === 'IDLE' || state === 'ERROR') {
      onStartListening();
    }
  };

  return (
    <div className="flex flex-col items-center justify-center my-4">
      {/* Outer ambient glow & ripple rings */}
      <div className="relative flex items-center justify-center">
        {state === 'LISTENING' && (
          <>
            <div className="absolute w-36 h-36 rounded-full bg-orange-500/20 animate-ping pointer-events-none" />
            <div className="absolute w-44 h-44 rounded-full bg-amber-500/10 animate-pulse pointer-events-none" />
          </>
        )}

        {state === 'SPEAKING' && (
          <div className="absolute w-36 h-36 rounded-full bg-emerald-500/20 animate-pulse pointer-events-none" />
        )}

        {/* Main Microphone Button */}
        <button
          onClick={handleClick}
          aria-label="Voice interaction button"
          className={`
            relative z-10 w-24 h-24 rounded-full flex items-center justify-center
            transition-all duration-300 shadow-2xl cursor-pointer
            ${
              state === 'LISTENING'
                ? 'bg-gradient-to-tr from-orange-600 to-amber-500 text-white ring-8 ring-orange-500/30 scale-105 shadow-orange-500/50'
                : state === 'PROCESSING'
                ? 'bg-gradient-to-tr from-indigo-600 to-purple-600 text-white ring-4 ring-indigo-500/30 shadow-indigo-500/40'
                : state === 'SPEAKING'
                ? 'bg-gradient-to-tr from-emerald-600 to-teal-500 text-white ring-8 ring-emerald-500/30 scale-105 shadow-emerald-500/50'
                : state === 'ERROR'
                ? 'bg-gradient-to-tr from-red-600 to-rose-500 text-white ring-4 ring-red-500/30'
                : 'bg-gradient-to-tr from-amber-500 to-orange-600 text-white hover:scale-105 ring-4 ring-amber-500/20 shadow-amber-500/30 hover:shadow-orange-500/50'
            }
          `}
        >
          {state === 'LISTENING' && <Mic className="w-10 h-10 animate-pulse" />}
          {state === 'PROCESSING' && <Loader2 className="w-10 h-10 animate-spin" />}
          {state === 'SPEAKING' && <Volume2 className="w-10 h-10 animate-bounce" />}
          {state === 'ERROR' && <AlertCircle className="w-10 h-10" />}
          {state === 'IDLE' && <Mic className="w-10 h-10" />}
        </button>
      </div>

      {/* Spoken waveform visualizer when speaking */}
      {state === 'SPEAKING' && (
        <div className="flex items-center gap-1.5 mt-4">
          <div className="w-1.5 bg-emerald-400 rounded-full animate-wave-bar" style={{ animationDelay: '0ms' }} />
          <div className="w-1.5 bg-emerald-400 rounded-full animate-wave-bar" style={{ animationDelay: '150ms' }} />
          <div className="w-1.5 bg-emerald-400 rounded-full animate-wave-bar" style={{ animationDelay: '300ms' }} />
          <div className="w-1.5 bg-emerald-400 rounded-full animate-wave-bar" style={{ animationDelay: '450ms' }} />
          <div className="w-1.5 bg-emerald-400 rounded-full animate-wave-bar" style={{ animationDelay: '600ms' }} />
          <button
            onClick={onStopSpeaking}
            className="ml-3 text-xs bg-gray-800 hover:bg-gray-700 text-emerald-400 px-2.5 py-1 rounded-full border border-emerald-500/30 flex items-center gap-1"
          >
            <Square className="w-3 h-3 fill-current" /> Stop Spoken Audio
          </button>
        </div>
      )}

      {/* Stop / Send immediately button when listening */}
      {state === 'LISTENING' && (
        <div className="flex items-center gap-2 mt-3">
          <button
            onClick={onStopListening}
            className="px-3.5 py-1.5 rounded-full bg-orange-600 hover:bg-orange-500 text-white text-xs font-bold shadow-lg shadow-orange-600/30 flex items-center gap-1.5 cursor-pointer transition-all animate-pulse"
          >
            <Square className="w-3 h-3 fill-current" /> Done Speaking (Send Now)
          </button>
        </div>
      )}

      {/* Status hint text */}
      <p className="mt-3 text-sm font-medium text-gray-300 tracking-wide">
        {state === 'LISTENING' && 'Listening... Keep speaking, or pause when finished'}
        {state === 'PROCESSING' && 'Understanding your voice query...'}
        {state === 'SPEAKING' && 'Speaking response... (Tap to interrupt)'}
        {state === 'ERROR' && 'Tap to retry microphone'}
        {state === 'IDLE' && 'Tap and speak'}
      </p>
    </div>
  );
};
