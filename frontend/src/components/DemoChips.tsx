import React from 'react';
import { Sparkles, MessageSquareQuote } from 'lucide-react';

interface DemoChipsProps {
  onSelectQuery: (query: string) => void;
}

const DEMO_QUERIES = [
  "Running shoes dikhao under 3000",
  "Mujhe black sneakers chahiye",
  "Iska discount kitna hai?",
  "Ye shoes size 9 mein available hai kya?",
  "Compare Sprint X and Runner Pro",
  "Which headphones have noise cancellation?",
  "Budget 2500 hai, kuch achha suggest karo",
  "Can you show me something cheaper?"
];

export const DemoChips: React.FC<DemoChipsProps> = ({ onSelectQuery }) => {
  return (
    <div className="max-w-4xl mx-auto px-4 my-4">
      <div className="flex items-center gap-1.5 mb-2 text-xs font-semibold text-gray-400">
        <Sparkles className="w-3.5 h-3.5 text-amber-400" />
        <span>Try these voice / Hinglish queries:</span>
      </div>

      <div className="flex flex-wrap gap-2">
        {DEMO_QUERIES.map((query, idx) => (
          <button
            key={idx}
            onClick={() => onSelectQuery(query)}
            className="text-xs bg-gray-900 hover:bg-gray-800 text-gray-300 hover:text-amber-300 px-3 py-1.5 rounded-full border border-gray-800 hover:border-amber-500/40 transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <MessageSquareQuote className="w-3 h-3 text-amber-500" />
            <span>{query}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
