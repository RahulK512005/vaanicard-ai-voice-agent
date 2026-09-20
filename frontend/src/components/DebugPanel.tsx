import React from 'react';
import { Terminal, Clock, Database, Brain, Tag, CheckCircle, AlertTriangle } from 'lucide-react';
import { DebugInfo } from '../types/conversation';

interface DebugPanelProps {
  debugInfo: DebugInfo | null;
  isOpen: boolean;
  onToggle: () => void;
}

export const DebugPanel: React.FC<DebugPanelProps> = ({ debugInfo, isOpen, onToggle }) => {
  return (
    <div className="fixed bottom-4 right-4 z-40">
      {/* Drawer Toggle Pill */}
      <button
        onClick={onToggle}
        className="px-3.5 py-2 rounded-full bg-gray-900 border border-gray-700 text-xs font-mono font-medium text-amber-400 hover:text-amber-300 shadow-xl flex items-center gap-2 transition-all hover:border-amber-500 cursor-pointer"
      >
        <Terminal className="w-3.5 h-3.5 text-amber-400" />
        <span>Dev Inspector {isOpen ? '▲' : '▼'}</span>
      </button>

      {/* Expanded Inspector Modal / Popover */}
      {isOpen && (
        <div className="absolute bottom-12 right-0 w-96 max-h-[70vh] bg-gray-950/95 backdrop-blur-md border border-gray-800 rounded-2xl shadow-2xl p-4 overflow-y-auto font-mono text-xs text-gray-300 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-gray-800">
            <span className="font-bold text-white flex items-center gap-1.5">
              <Terminal className="w-4 h-4 text-amber-400" /> Observability & Latency
            </span>
            <span className="text-[10px] bg-gray-800 px-2 py-0.5 rounded text-gray-400">
              Session: {debugInfo?.session_id ? debugInfo.session_id.slice(0, 10) + '...' : 'N/A'}
            </span>
          </div>

          {!debugInfo ? (
            <p className="text-gray-500 italic">No interaction logged yet. Speak or type a query to inspect live pipeline data.</p>
          ) : (
            <>
              {/* Intent & Language */}
              <div className="space-y-1.5 bg-gray-900/60 p-2.5 rounded-lg border border-gray-800">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 flex items-center gap-1"><Brain className="w-3 h-3 text-purple-400" /> Intent:</span>
                  <span className="text-amber-400 font-bold">{debugInfo.detected_intent}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Language:</span>
                  <span className="text-emerald-400 font-semibold">{debugInfo.detected_language}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Validation:</span>
                  <span className={debugInfo.validation_passed ? "text-emerald-400" : "text-amber-400"}>
                    {debugInfo.validation_passed ? "Passed" : "Sanitized"}
                  </span>
                </div>
              </div>

              {/* Extracted Entities */}
              <div className="space-y-1 bg-gray-900/60 p-2.5 rounded-lg border border-gray-800">
                <span className="text-gray-400 flex items-center gap-1 mb-1"><Tag className="w-3 h-3 text-cyan-400" /> Entities:</span>
                <pre className="text-[11px] text-gray-300 overflow-x-auto">
                  {JSON.stringify(debugInfo.extracted_entities, null, 2)}
                </pre>
              </div>

              {/* Authoritative Pricing */}
              {debugInfo.pricing_authoritative && (
                <div className="space-y-1 bg-gray-900/60 p-2.5 rounded-lg border border-gray-800">
                  <span className="text-gray-400 flex items-center gap-1 text-emerald-400 font-bold mb-1">
                    <CheckCircle className="w-3 h-3" /> Authoritative Pricing (Backend Logic):
                  </span>
                  <div className="text-[11px] space-y-0.5">
                    <div>MRP: ₹{debugInfo.pricing_authoritative.original_mrp}</div>
                    <div>Base Price: ₹{debugInfo.pricing_authoritative.base_price}</div>
                    <div>Coupon: {debugInfo.pricing_authoritative.coupon_code || 'None'} (-₹{debugInfo.pricing_authoritative.coupon_discount})</div>
                    <div className="font-bold text-white">Net Payable: ₹{debugInfo.pricing_authoritative.final_payable}</div>
                  </div>
                </div>
              )}

              {/* RAG Context */}
              <div className="space-y-1 bg-gray-900/60 p-2.5 rounded-lg border border-gray-800">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400 flex items-center gap-1"><Database className="w-3 h-3 text-blue-400" /> FAISS RAG:</span>
                  <span className={debugInfo.rag_used ? "text-emerald-400 font-semibold" : "text-gray-500"}>
                    {debugInfo.rag_used ? "Active" : "Bypassed"}
                  </span>
                </div>
                {debugInfo.rag_sources && debugInfo.rag_sources.length > 0 && (
                  <div className="text-[10px] text-gray-400 mt-1">
                    Sources: {debugInfo.rag_sources.join(', ')}
                  </div>
                )}
              </div>

              {/* Latency Breakdown */}
              <div className="space-y-1 bg-gray-900/60 p-2.5 rounded-lg border border-gray-800">
                <span className="text-gray-400 flex items-center gap-1 mb-1"><Clock className="w-3 h-3 text-orange-400" /> Pipeline Latency:</span>
                <div className="grid grid-cols-2 gap-1 text-[10px]">
                  <div>Intent: {debugInfo.latency.intent_ms}ms</div>
                  <div>Retrieval: {debugInfo.latency.retrieval_ms}ms</div>
                  <div>Pricing: {debugInfo.latency.pricing_ms}ms</div>
                  <div>LLM: {debugInfo.latency.llm_ms}ms</div>
                  <div>Validation: {debugInfo.latency.validation_ms}ms</div>
                  <div className="font-bold text-amber-400">Total: {debugInfo.latency.total_ms}ms</div>
                </div>
              </div>

              {/* Prompt Version */}
              <div className="text-[10px] text-gray-500 truncate">
                Prompt: {debugInfo.prompt_version}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};
