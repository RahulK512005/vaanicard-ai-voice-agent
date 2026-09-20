import React from 'react';
import { Star, CheckCircle, AlertCircle, Scale, MessageSquare, Tag, Eye } from 'lucide-react';
import { Product } from '../types/product';

interface ProductCardProps {
  product: Product;
  isSelectedForCompare?: boolean;
  onCompareToggle?: (product: Product) => void;
  onAskAI?: (product: Product) => void;
  onViewDetails?: (product: Product) => void;
}

// Visual category color & placeholder banner
const CATEGORY_COLORS: Record<string, string> = {
  'Running Shoes': 'from-blue-600 to-cyan-500',
  'Sneakers': 'from-purple-600 to-pink-500',
  'Headphones': 'from-amber-600 to-orange-500',
  'Smart Watches': 'from-emerald-600 to-teal-500',
  'Backpacks': 'from-indigo-600 to-blue-500',
  'T-Shirts': 'from-rose-600 to-red-500',
  'Laptops': 'from-slate-700 to-zinc-600',
  'Mobile Accessories': 'from-violet-600 to-fuchsia-500'
};

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  isSelectedForCompare = false,
  onCompareToggle,
  onAskAI,
  onViewDetails
}) => {
  const gradient = CATEGORY_COLORS[product.category] || 'from-orange-600 to-amber-500';

  return (
    <div className="bg-gray-900/90 border border-gray-800 rounded-2xl overflow-hidden hover:border-amber-500/40 transition-all duration-300 hover:shadow-xl hover:shadow-amber-500/5 flex flex-col justify-between group">
      {/* Card Header / Image simulation */}
      <div>
        <div className={`h-36 bg-gradient-to-br ${gradient} p-4 flex flex-col justify-between relative overflow-hidden`}>
          <div className="flex items-center justify-between z-10">
            <span className="bg-black/40 backdrop-blur text-white text-xs px-2.5 py-1 rounded-full font-medium">
              {product.brand}
            </span>
            <span className="bg-amber-400 text-gray-950 text-xs px-2 py-0.5 rounded-full font-bold shadow">
              {product.discount_percentage}% OFF
            </span>
          </div>

          <div className="z-10">
            <span className="text-xs uppercase tracking-wider text-white/80 font-semibold">
              {product.category}
            </span>
            <h3 className="text-white font-bold text-lg line-clamp-1 group-hover:text-amber-200 transition-colors">
              {product.name}
            </h3>
          </div>

          {/* Abstract background design element */}
          <div className="absolute -right-6 -bottom-6 w-28 h-28 rounded-full bg-white/10 blur-xl pointer-events-none" />
        </div>

        {/* Card Body */}
        <div className="p-4 space-y-3">
          {/* Price & Rating Row */}
          <div className="flex items-baseline justify-between">
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-extrabold text-white">
                ₹{product.price.toLocaleString('en-IN')}
              </span>
              <span className="text-xs text-gray-500 line-through">
                ₹{product.original_price.toLocaleString('en-IN')}
              </span>
            </div>

            <div className="flex items-center gap-1 bg-gray-800/80 px-2 py-0.5 rounded-md text-xs font-semibold text-amber-400 border border-gray-700">
              <Star className="w-3.5 h-3.5 fill-current" />
              <span>{product.rating}</span>
            </div>
          </div>

          {/* Standout Feature */}
          <p className="text-xs text-gray-300 line-clamp-2 leading-relaxed">
            {product.features && product.features.length > 0
              ? product.features[0]
              : product.description}
          </p>

          {/* Color and Stock Info */}
          <div className="flex items-center justify-between text-xs text-gray-400 pt-1 border-t border-gray-800">
            <span>Color: <strong className="text-gray-200 font-medium">{product.color}</strong></span>
            {product.stock > 0 ? (
              <span className="text-emerald-400 flex items-center gap-1">
                <CheckCircle className="w-3 h-3" /> In Stock ({product.stock})
              </span>
            ) : (
              <span className="text-rose-400 flex items-center gap-1">
                <AlertCircle className="w-3 h-3" /> Out of Stock
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Card Actions Footer */}
      <div className="p-4 pt-0 grid grid-cols-3 gap-1.5 border-t border-gray-800/50">
        <button
          onClick={() => onCompareToggle && onCompareToggle(product)}
          className={`px-2 py-2 text-xs font-medium rounded-lg flex items-center justify-center gap-1 transition-colors cursor-pointer ${
            isSelectedForCompare
              ? 'bg-amber-500 text-gray-950 font-bold'
              : 'bg-gray-800 hover:bg-gray-700 text-gray-300'
          }`}
          title="Compare product"
        >
          <Scale className="w-3.5 h-3.5" />
          <span>{isSelectedForCompare ? 'Added' : 'Compare'}</span>
        </button>

        <button
          onClick={() => onAskAI && onAskAI(product)}
          className="px-2 py-2 text-xs font-medium rounded-lg bg-orange-600/20 hover:bg-orange-600/30 text-orange-300 border border-orange-500/30 flex items-center justify-center gap-1 transition-colors cursor-pointer"
          title="Ask AI about this product"
        >
          <MessageSquare className="w-3.5 h-3.5" />
          <span>Ask AI</span>
        </button>

        <button
          onClick={() => onViewDetails && onViewDetails(product)}
          className="px-2 py-2 text-xs font-medium rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 flex items-center justify-center gap-1 transition-colors cursor-pointer"
          title="View product details and specs"
        >
          <Eye className="w-3.5 h-3.5" />
          <span>Details</span>
        </button>
      </div>
    </div>
  );
};
