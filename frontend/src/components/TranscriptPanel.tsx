import React from 'react';
import { Mic, Sparkles } from 'lucide-react';
import { VoiceState } from '../types/conversation';

interface TranscriptPanelProps {
  transcript: string;
  interimTranscript: string;
  state: VoiceState;
  lastUserQuery?: string;
}

export const TranscriptPanel: React.FC<TranscriptPanelProps> = ({
  transcript,
  interimTranscript,
  state,
  lastUserQuery
}) => {
  const currentSpeech = transcript || interimTranscript;

  if (state === 'IDLE' && !currentSpeech && !lastUserQuery) {
    return (
      <div className="max-w-xl mx-auto px-4 py-2 text-center text-xs text-gray-400 bg-gray-900/40 rounded-full border border-gray-800">
        Try saying: <span className="text-amber-400 font-medium">"Running shoes dikhao under 3000"</span> or <span className="text-amber-400 font-medium">"Mujhe black sneakers chahiye"</span>
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto w-full px-4 mb-3">
      <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-xl p-3 shadow-lg flex items-start gap-3">
        <div className={`p-2 rounded-lg ${state === 'LISTENING' ? 'bg-orange-500/20 text-orange-400 animate-pulse' : 'bg-gray-800 text-gray-400'}`}>
          <Mic className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 mb-1">
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              {state === 'LISTENING' ? 'Live Voice Stream' : 'Voice Input'}
            </span>
            {state === 'LISTENING' && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-orange-500/10 text-orange-400 border border-orange-500/20">
                Listening...
              </span>
            )}
          </div>
          <p className="text-sm sm:text-base text-gray-100 font-medium leading-relaxed">
            {transcript && <span>{transcript} </span>}
            {interimTranscript && (
              <span className="text-amber-300 italic">{interimTranscript} </span>
            )}
            {!transcript && !interimTranscript && (
              <span className="text-gray-400">{lastUserQuery || 'Listening for your voice...'}</span>
            )}
            {state === 'LISTENING' && (
              <span className="inline-block w-2 h-2 ml-1 bg-orange-400 rounded-full animate-ping" />
            )}
          </p>
        </div>
      </div>
    </div>
  );
};
