import { useState, useRef, useCallback } from 'react';
import { VoiceState } from '../types/conversation';

// Extend window for Web Speech API
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

interface UseVoiceOptions {
  onFinalTranscript?: (transcript: string) => void;
  language?: string; // 'en-IN' or 'hi-IN'
  silenceTimeoutMs?: number; // silence duration before automatically finalizing
}

export function useVoice({
  onFinalTranscript,
  language = 'en-IN',
  silenceTimeoutMs = 1500
}: UseVoiceOptions = {}) {
  const [state, setState] = useState<VoiceState>('IDLE');
  const [transcript, setTranscript] = useState<string>('');
  const [interimTranscript, setInterimTranscript] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const SpeechRecognition = typeof window !== 'undefined'
    ? (window.SpeechRecognition || window.webkitSpeechRecognition)
    : null;
  const isSupported = Boolean(SpeechRecognition);

  const recognitionRef = useRef<any>(null);
  const isSpeakingRef = useRef<boolean>(false);
  const silenceTimerRef = useRef<any>(null);
  const accumulatedTextRef = useRef<string>('');

  const stopSpeaking = useCallback(() => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    isSpeakingRef.current = false;
    setState(prev => (prev === 'SPEAKING' ? 'IDLE' : prev));
  }, []);

  const commitTranscript = useCallback((textToCommit: string) => {
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }

    const trimmed = textToCommit.trim();
    if (trimmed.length < 2) {
      // Too short / empty noise, smoothly return to IDLE
      setState('IDLE');
      setTranscript('');
      setInterimTranscript('');
      return;
    }

    setTranscript(trimmed);
    setInterimTranscript('');
    setState('PROCESSING');

    // Stop recognition
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {
        // ignore
      }
      recognitionRef.current = null;
    }

    if (onFinalTranscript) {
      onFinalTranscript(trimmed);
    }
  }, [onFinalTranscript]);

  const stopListening = useCallback(() => {
    // User explicitly tapped button to stop and submit what was said
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }

    const fullText = (accumulatedTextRef.current || transcript || interimTranscript).trim();
    if (fullText) {
      commitTranscript(fullText);
    } else {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {
          // ignore
        }
        recognitionRef.current = null;
      }
      setState('IDLE');
    }
  }, [commitTranscript, transcript, interimTranscript]);

  const startListening = useCallback(() => {
    // 1. Interrupt any current TTS playback
    stopSpeaking();

    // Reset speech state
    accumulatedTextRef.current = '';
    setTranscript('');
    setInterimTranscript('');
    setErrorMessage(null);

    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }

    if (!SpeechRecognition) {
      setErrorMessage('Web Speech API is not supported in this browser. Please use Google Chrome or Microsoft Edge.');
      setState('ERROR');
      return;
    }

    // Clean up any existing recognition instance
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch (e) {
        // ignore
      }
      recognitionRef.current = null;
    }

    try {
      const recognition = new SpeechRecognition();
      // CONTINUOUS = true allows user to pause naturally without prematurely cutting off!
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = language;

      recognition.onstart = () => {
        setState('LISTENING');
        setErrorMessage(null);
        setInterimTranscript('');
        accumulatedTextRef.current = '';
      };

      recognition.onresult = (event: any) => {
        let finalConcat = '';
        let interimConcat = '';

        for (let i = 0; i < event.results.length; ++i) {
          const item = event.results[i];
          if (item.isFinal) {
            finalConcat += item[0].transcript + ' ';
          } else {
            interimConcat += item[0].transcript;
          }
        }

        const fullSentence = (finalConcat + interimConcat).trim();
        accumulatedTextRef.current = fullSentence;
        setTranscript(finalConcat.trim());
        setInterimTranscript(interimConcat.trim());

        // Reset the silence debounce timer
        if (silenceTimerRef.current) {
          clearTimeout(silenceTimerRef.current);
        }

        // When user stops speaking for silenceTimeoutMs (e.g. 1500ms), finalize and answer!
        if (fullSentence.length > 1) {
          silenceTimerRef.current = setTimeout(() => {
            commitTranscript(accumulatedTextRef.current);
          }, silenceTimeoutMs);
        }
      };

      recognition.onerror = (event: any) => {
        const err = event.error;
        if (err === 'aborted' || err === 'no-speech') {
          // If we already have accumulated text, commit it rather than dropping
          if (accumulatedTextRef.current.trim().length > 2) {
            commitTranscript(accumulatedTextRef.current);
            return;
          }
          setState('IDLE');
          setErrorMessage(null);
          return;
        }

        if (err === 'not-allowed' || err === 'service-not-allowed') {
          setErrorMessage('Microphone access was denied. Please click the camera/mic icon in the browser URL bar to allow access.');
          setState('ERROR');
        } else if (err === 'audio-capture') {
          setErrorMessage('No microphone detected. Please check your audio input device.');
          setState('ERROR');
        } else if (err === 'network') {
          setErrorMessage('Network connection error during voice recognition.');
          setState('IDLE');
        } else {
          setErrorMessage(`Speech recognition error: ${err}`);
          setState('IDLE');
        }
      };

      recognition.onend = () => {
        recognitionRef.current = null;
        // If recognition closed automatically and we have speech accumulated, commit it
        if (accumulatedTextRef.current.trim().length > 2) {
          commitTranscript(accumulatedTextRef.current);
        } else {
          setState(prev => (prev === 'LISTENING' ? 'IDLE' : prev));
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (e: any) {
      console.warn('Recognition start exception:', e);
      setErrorMessage('Could not initialize microphone. Please tap again.');
      setState('IDLE');
    }
  }, [SpeechRecognition, language, silenceTimeoutMs, stopSpeaking, commitTranscript]);

  const speak = useCallback((text: string, langCode: string = 'en-IN', onEnd?: () => void) => {
    if (!('speechSynthesis' in window)) {
      console.warn('SpeechSynthesis is not supported.');
      return;
    }

    // Stop previous utterance
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = langCode;
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    const voices = window.speechSynthesis.getVoices();
    const indianVoice = voices.find(v => v.lang.includes('IN') || v.name.includes('India') || v.name.includes('Hindi'));
    if (indianVoice) {
      utterance.voice = indianVoice;
    }

    utterance.onstart = () => {
      isSpeakingRef.current = true;
      setState('SPEAKING');
    };

    utterance.onend = () => {
      isSpeakingRef.current = false;
      setState('IDLE');
      if (onEnd) onEnd();
    };

    utterance.onerror = (e) => {
      console.warn('TTS error:', e);
      isSpeakingRef.current = false;
      setState('IDLE');
    };

    window.speechSynthesis.speak(utterance);
  }, []);

  return {
    state,
    setState,
    transcript,
    interimTranscript,
    errorMessage,
    isSupported,
    startListening,
    stopListening,
    speak,
    stopSpeaking
  };
}
