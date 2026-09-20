import React from 'react';
import { X, Check, Scale, Volume2, Trophy, ArrowRight } from 'lucide-react';
import { Product, ComparisonData } from '../types/product';

interface ComparisonPanelProps {
  products: Product[];
  comparisonData?: ComparisonData | null;
  onClose: () => void;
  onSpeakSummary?: (text: string) => void;
}

export const ComparisonPanel: React.FC<ComparisonPanelProps> = ({
  products,
  comparisonData,
  onClose,
  onSpeakSummary
}) => {
  if (products.length < 2) return null;

  const p1 = products[0];
  const p2 = products[1];

  const priceDiff = Math.abs(p1.price - p2.price);
  const cheaper = p1.price <= p2.price ? p1 : p2;
  const higherRated = p1.rating >= p2.rating ? p1 : p2;

  const comparisonSpeech = (
    `${p1.name} is ₹${p1.price.toLocaleString('en-IN')}, while ${p2.name} is ₹${p2.price.toLocaleString('en-IN')}. ` +
    `${cheaper.name} is more affordable by ₹${priceDiff.toLocaleString('en-IN')}. ` +
    `Which matters more to you, price or user rating?`
  );

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-gray-900 border border-gray-800 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl p-6 relative">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-gray-800">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-amber-500/20 text-amber-400">
              <Scale className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">AI Product Comparison</h2>
              <p className="text-xs text-gray-400">Side-by-side trade-offs powered by VaaniCart AI</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* AI Voice Highlight Banner */}
        <div className="mt-4 p-4 rounded-xl bg-gradient-to-r from-amber-500/10 via-orange-500/10 to-transparent border border-amber-500/20 flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <Trophy className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-amber-300">Spoken Comparison Summary</h4>
              <p className="text-sm text-gray-200 mt-1">{comparisonSpeech}</p>
            </div>
          </div>
          {onSpeakSummary && (
            <button
              onClick={() => onSpeakSummary(comparisonSpeech)}
              className="px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-gray-950 text-xs font-bold flex items-center gap-1 shrink-0 shadow cursor-pointer"
            >
              <Volume2 className="w-3.5 h-3.5" /> Listen
            </button>
          )}
        </div>

        {/* Side-by-Side Comparison Matrix */}
        <div className="mt-6 grid grid-cols-2 gap-4">
          {[p1, p2].map((p, idx) => {
            const isCheaper = p.id === cheaper.id;
            const isHigherRated = p.id === higherRated.id;

            return (
              <div
                key={p.id}
                className={`p-5 rounded-xl border ${
                  isCheaper ? 'border-emerald-500/40 bg-emerald-950/10' : 'border-gray-800 bg-gray-850/50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider">
                    Option {idx + 1}
                  </span>
                  {isCheaper && (
                    <span className="text-xs bg-emerald-500/20 text-emerald-300 font-bold px-2 py-0.5 rounded-full border border-emerald-500/30">
                      Best Value
                    </span>
                  )}
                </div>

                <h3 className="text-lg font-bold text-white mt-1">{p.name}</h3>
                <p className="text-xs text-gray-400">{p.brand} • {p.category}</p>

                <div className="mt-3 flex items-baseline gap-2">
                  <span className="text-2xl font-extrabold text-white">
                    ₹{p.price.toLocaleString('en-IN')}
                  </span>
                  <span className="text-xs text-gray-500 line-through">
                    ₹{p.original_price.toLocaleString('en-IN')}
                  </span>
                  <span className="text-xs text-amber-400 font-bold">
                    {p.discount_percentage}% OFF
                  </span>
                </div>

                <div className="mt-4 space-y-2 text-xs">
                  <div className="flex justify-between py-1.5 border-b border-gray-800">
                    <span className="text-gray-400">User Rating</span>
                    <span className="text-white font-semibold flex items-center gap-1">
                      ⭐ {p.rating} / 5
                    </span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-gray-800">
                    <span className="text-gray-400">Available Color</span>
                    <span className="text-white font-semibold">{p.color}</span>
                  </div>
                  <div className="flex justify-between py-1.5 border-b border-gray-800">
                    <span className="text-gray-400">Stock Units</span>
                    <span className="text-emerald-400 font-semibold">{p.stock} units</span>
                  </div>
                  <div className="py-2">
                    <span className="text-gray-400 block mb-1">Key Specifications:</span>
                    <ul className="space-y-1">
                      {p.features.map((feat, fIdx) => (
                        <li key={fIdx} className="text-gray-300 flex items-start gap-1.5">
                          <Check className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                          <span>{feat}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Action Footer */}
        <div className="mt-6 flex justify-end gap-3 pt-4 border-t border-gray-800">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm font-medium transition-colors cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
