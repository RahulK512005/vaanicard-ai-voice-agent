import { useState, useCallback, useEffect } from 'react';
import { ChatMessage, DebugInfo } from '../types/conversation';
import { Product, ComparisonData } from '../types/product';
import { sendChatMessage, fetchProducts } from '../services/api';
import { fallbackProducts } from '../data/fallbackProducts';

export function useConversation() {
  const [sessionId, setSessionId] = useState<string>(() => {
    return localStorage.getItem('vaanicart_session_id') || `sess_${Date.now()}`;
  });
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  // Immediately initialize with fallback products so user never sees a blank screen
  const [displayedProducts, setDisplayedProducts] = useState<Product[]>(() => fallbackProducts.slice(0, 12));
  const [comparison, setComparison] = useState<ComparisonData | null>(null);
  const [debugInfo, setDebugInfo] = useState<DebugInfo | null>(null);
  const [activeProductId, setActiveProductId] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    localStorage.setItem('vaanicart_session_id', sessionId);
  }, [sessionId]);

  // Sync with live backend catalog on mount
  useEffect(() => {
    fetchProducts(undefined, 12)
      .then(prods => {
        if (prods && prods.length > 0) {
          setDisplayedProducts(prods);
        }
      })
      .catch(err => console.warn('Could not load initial catalog from server:', err));
  }, []);

  const processQuery = useCallback(async (
    query: string,
    isVoice: boolean = true,
    onAssistantSpoken?: (spokenText: string, langCode: string) => void
  ) => {
    if (!query.trim()) return;

    // 1. Add user message
    const userMsg: ChatMessage = {
      id: `usr_${Date.now()}`,
      sender: 'user',
      text: query,
      timestamp: new Date(),
      isVoiceInput: isVoice
    };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage(
        query,
        sessionId,
        activeProductId
      );

      // Update state
      if (response.session_id) {
        setSessionId(response.session_id);
      }

      if (response.products && response.products.length > 0) {
        setDisplayedProducts(response.products);
        setActiveProductId(response.products[0].id);
      }

      if (response.comparison) {
        setComparison(response.comparison);
      } else {
        setComparison(null);
      }

      if (response.debug) {
        setDebugInfo(response.debug);
      }

      // Add assistant message
      const assistantMsg: ChatMessage = {
        id: `ast_${Date.now()}`,
        sender: 'assistant',
        text: response.display_response,
        timestamp: new Date(),
        spokenOutput: response.spoken_response,
        products: response.products,
        comparison: response.comparison,
        debug: response.debug
      };
      setMessages(prev => [...prev, assistantMsg]);

      // Trigger TTS playback
      if (onAssistantSpoken && response.spoken_response) {
        onAssistantSpoken(
          response.spoken_response.text,
          response.spoken_response.language_code || 'en-IN'
        );
      }

      return response;
    } catch (err: any) {
      console.error('Conversation query failed:', err);
      const errorMsg: ChatMessage = {
        id: `err_${Date.now()}`,
        sender: 'assistant',
        text: 'Sorry, I had trouble connecting to the server. Please check your backend connection.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, activeProductId]);

  const selectContextProduct = useCallback((product: Product) => {
    setActiveProductId(product.id);
  }, []);

  const clearHistory = useCallback(() => {
    setMessages([]);
    setComparison(null);
    setDebugInfo(null);
    setActiveProductId(undefined);
    setSessionId(`sess_${Date.now()}`);
  }, []);

  return {
    sessionId,
    messages,
    displayedProducts,
    setDisplayedProducts,
    comparison,
    setComparison,
    debugInfo,
    activeProductId,
    isLoading,
    processQuery,
    selectContextProduct,
    clearHistory
  };
}
