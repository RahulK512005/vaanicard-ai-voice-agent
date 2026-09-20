import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, RotateCcw, Send, AlertCircle, ShoppingBag } from 'lucide-react';
import { useVoice } from './hooks/useVoice';
import { useConversation } from './hooks/useConversation';
import { VoiceButton } from './components/VoiceButton';
import { TranscriptPanel } from './components/TranscriptPanel';
import { ProductGrid } from './components/ProductGrid';
import { ComparisonPanel } from './components/ComparisonPanel';
import { ProductDetailsModal } from './components/ProductDetailsModal';
import { ChatMessage } from './components/ChatMessage';
import { DebugPanel } from './components/DebugPanel';
import { DemoChips } from './components/DemoChips';
import { Product } from './types/product';
import { fetchProducts } from './services/api';

export function App() {
  const [typedInput, setTypedInput] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [compareList, setCompareList] = useState<Product[]>([]);
  const [showComparisonModal, setShowComparisonModal] = useState<boolean>(false);
  const [detailedProduct, setDetailedProduct] = useState<Product | null>(null);
  const [isDebugOpen, setIsDebugOpen] = useState<boolean>(false);
  const [showChatHistory, setShowChatHistory] = useState<boolean>(false);
  const [speechLanguage, setSpeechLanguage] = useState<string>('en-IN');

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    sessionId,
    messages,
    displayedProducts,
    setDisplayedProducts,
    comparison,
    setComparison,
    debugInfo,
    isLoading,
    processQuery,
    selectContextProduct,
    clearHistory
  } = useConversation();

  const {
    state: voiceState,
    setState: setVoiceState,
    transcript,
    interimTranscript,
    errorMessage: voiceError,
    startListening,
    stopListening,
    speak,
    stopSpeaking
  } = useVoice({
    language: speechLanguage,
    silenceTimeoutMs: 1600,
    onFinalTranscript: (text) => {
      handleQuerySubmit(text, true);
    }
  });

  const handleQuerySubmit = async (queryText: string, isVoice: boolean = false) => {
    if (!queryText.trim()) return;
    setVoiceState('PROCESSING');

    await processQuery(queryText, isVoice, (spokenText, langCode) => {
      // Trigger voice TTS output
      speak(spokenText, langCode);
    });
  };

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (typedInput.trim()) {
      handleQuerySubmit(typedInput.trim(), false);
      setTypedInput('');
    }
  };

  const handleCategorySelect = async (category: string) => {
    setSelectedCategory(category);
    try {
      const prods = await fetchProducts(category === 'All' ? undefined : category, 12);
      setDisplayedProducts(prods);
    } catch (err) {
      console.warn('Category filter error:', err);
    }
  };

  const handleCompareToggle = (product: Product) => {
    setCompareList(prev => {
      const exists = prev.some(p => p.id === product.id);
      if (exists) {
        return prev.filter(p => p.id !== product.id);
      } else {
        if (prev.length >= 2) {
          return [prev[1], product];
        }
        const updated = [...prev, product];
        if (updated.length === 2) {
          setShowComparisonModal(true);
        }
        return updated;
      }
    });
  };

  const handleAskAIAboutProduct = (product: Product) => {
    selectContextProduct(product);
    const query = `Tell me more about ${product.name} and what discount is available.`;
    handleQuerySubmit(query, false);
  };

  // Scroll to bottom of chat when new message arrives
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  return (
    <div className="min-h-screen bg-[#0b0f19] text-gray-100 flex flex-col justify-between selection:bg-amber-500 selection:text-black">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-30 bg-gray-950/80 backdrop-blur-md border-b border-gray-800 px-4 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-orange-600 flex items-center justify-center text-white shadow-lg shadow-amber-500/20">
              <ShoppingBag className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-extrabold tracking-tight text-white">
                  VaaniCart <span className="text-amber-400">AI</span>
                </h1>
                <span className="text-[10px] bg-amber-400/10 text-amber-400 border border-amber-400/20 px-2 py-0.5 rounded-full font-bold uppercase tracking-wider">
                  Voice Commerce
                </span>
              </div>
              <p className="text-xs text-gray-400">
                Your AI Shopping Assistant — Just Ask.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Language Switcher */}
            <button
              onClick={() => setSpeechLanguage(prev => (prev === 'en-IN' ? 'hi-IN' : 'en-IN'))}
              title="Toggle speech recognition dialect"
              className="px-2.5 py-1 rounded-full bg-gray-900 hover:bg-gray-800 text-amber-300 border border-gray-800 text-xs font-semibold transition-colors cursor-pointer flex items-center gap-1"
            >
              <span>{speechLanguage === 'en-IN' ? '🇮🇳 Hinglish / English' : '🇮🇳 Hindi (हिन्दी)'}</span>
            </button>

            {/* Compare Drawer Indicator */}
            {compareList.length > 0 && (
              <button
                onClick={() => setShowComparisonModal(true)}
                className="px-3 py-1.5 rounded-full bg-amber-500 hover:bg-amber-400 text-gray-950 text-xs font-bold transition-all shadow-md cursor-pointer flex items-center gap-1.5"
              >
                <span>Compare ({compareList.length})</span>
              </button>
            )}

            {/* Conversation Drawer Toggle */}
            <button
              onClick={() => setShowChatHistory(!showChatHistory)}
              className="px-3 py-1.5 rounded-full bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-800 text-xs font-medium transition-colors flex items-center gap-1.5 cursor-pointer"
            >
              <MessageSquare className="w-3.5 h-3.5 text-amber-400" />
              <span>Conversation ({messages.length})</span>
            </button>

            {/* Reset Session */}
            <button
              onClick={() => {
                clearHistory();
                stopSpeaking();
              }}
              title="Reset Conversation Session"
              className="p-2 rounded-full bg-gray-900 hover:bg-gray-800 text-gray-400 hover:text-white border border-gray-800 transition-colors cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-6 space-y-8">
        {/* Error notification banner if any */}
        {voiceError && (
          <div className="max-w-2xl mx-auto p-3 rounded-xl bg-red-950/50 border border-red-800 text-red-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
            <span>{voiceError}</span>
          </div>
        )}

        {/* Central Voice Hero Section */}
        <div className="text-center py-4 relative">
          {/* Subtle Background Radial Glow */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 rounded-full bg-orange-500/5 blur-3xl pointer-events-none" />

          {/* Large Animated Microphone */}
          <VoiceButton
            state={voiceState}
            onStartListening={startListening}
            onStopListening={stopListening}
            onStopSpeaking={stopSpeaking}
          />

          {/* Live Transcript / Speech Stream Panel */}
          <TranscriptPanel
            transcript={transcript}
            interimTranscript={interimTranscript}
            state={voiceState}
            lastUserQuery={messages.filter(m => m.sender === 'user').slice(-1)[0]?.text}
          />

          {/* Quick Demo Hinglish / Voice Prompts */}
          <DemoChips onSelectQuery={(q) => handleQuerySubmit(q, false)} />

          {/* Text Input Fallback Bar */}
          <div className="max-w-xl mx-auto px-4 mt-4">
            <form onSubmit={handleTextSubmit} className="relative flex items-center">
              <input
                type="text"
                value={typedInput}
                onChange={(e) => setTypedInput(e.target.value)}
                placeholder="Or type in English or Hinglish (e.g. running shoes under 3000)..."
                className="w-full bg-gray-900/90 border border-gray-800 focus:border-amber-500 rounded-full py-2.5 pl-4 pr-12 text-sm text-gray-100 placeholder-gray-500 focus:outline-none shadow-inner"
              />
              <button
                type="submit"
                disabled={!typedInput.trim() || isLoading}
                className="absolute right-1.5 p-2 rounded-full bg-amber-500 hover:bg-amber-400 text-gray-950 font-bold disabled:opacity-30 disabled:cursor-not-allowed transition-all cursor-pointer shadow"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        </div>

        {/* Conversation Stream Modal / Drawer if open */}
        {showChatHistory && (
          <div className="bg-gray-900/90 border border-gray-800 rounded-2xl p-4 max-w-3xl mx-auto shadow-2xl space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-gray-800">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-amber-400" /> Multi-Turn Voice Dialogue
              </h3>
              <button
                onClick={() => setShowChatHistory(false)}
                className="text-xs text-gray-400 hover:text-white"
              >
                Hide
              </button>
            </div>
            <div className="max-h-72 overflow-y-auto space-y-2 pr-2">
              {messages.length === 0 ? (
                <p className="text-xs text-gray-500 text-center py-6">No messages yet. Speak above to start!</p>
              ) : (
                messages.map(msg => (
                  <ChatMessage
                    key={msg.id}
                    message={msg}
                    onReplayAudio={(txt) => speak(txt)}
                  />
                ))
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>
        )}

        {/* Product Catalog Grid Section */}
        <section className="space-y-4 pt-2">
          <div className="flex items-baseline justify-between">
            <div>
              <h2 className="text-xl font-bold text-white">Recommended Products</h2>
              <p className="text-xs text-gray-400">
                Found {displayedProducts.length} verified products in catalog
              </p>
            </div>
          </div>

          <ProductGrid
            products={displayedProducts}
            selectedCategory={selectedCategory}
            onSelectCategory={handleCategorySelect}
            compareList={compareList}
            onCompareToggle={handleCompareToggle}
            onAskAI={handleAskAIAboutProduct}
            onViewDetails={(p) => setDetailedProduct(p)}
          />
        </section>
      </main>

      {/* Comparison Modal */}
      {showComparisonModal && (
        <ComparisonPanel
          products={compareList}
          comparisonData={comparison}
          onClose={() => setShowComparisonModal(false)}
          onSpeakSummary={(txt) => speak(txt)}
        />
      )}

      {/* Product Details Modal */}
      {detailedProduct && (
        <ProductDetailsModal
          product={detailedProduct}
          onClose={() => setDetailedProduct(null)}
          onAskAIAboutThis={handleAskAIAboutProduct}
        />
      )}

      {/* Developer Observability & Latency Inspector */}
      <DebugPanel
        debugInfo={debugInfo}
        isOpen={isDebugOpen}
        onToggle={() => setIsDebugOpen(!isDebugOpen)}
      />

      {/* Footer */}
      <footer className="border-t border-gray-900 py-6 px-4 text-center text-xs text-gray-600">
        <p>VaaniCart AI — Production-Grade Voice AI E-Commerce Engine</p>
        <p className="mt-1 text-gray-500">STT (Web Speech) • FAISS RAG • Deterministic Pricing Engine • Hinglish NLU • TTS</p>
      </footer>
    </div>
  );
}

export default App;
