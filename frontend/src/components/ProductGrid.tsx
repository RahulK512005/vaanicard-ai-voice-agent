import React from 'react';
import { Product } from '../types/product';
import { ProductCard } from './ProductCard';
import { Layers, ShoppingBag } from 'lucide-react';

interface ProductGridProps {
  products: Product[];
  selectedCategory?: string;
  onSelectCategory?: (category: string) => void;
  compareList: Product[];
  onCompareToggle: (product: Product) => void;
  onAskAI: (product: Product) => void;
  onViewDetails: (product: Product) => void;
}

const CATEGORIES = [
  'All',
  'Running Shoes',
  'Sneakers',
  'Headphones',
  'Smart Watches',
  'Backpacks',
  'T-Shirts',
  'Laptops',
  'Mobile Accessories'
];

export const ProductGrid: React.FC<ProductGridProps> = ({
  products,
  selectedCategory = 'All',
  onSelectCategory,
  compareList,
  onCompareToggle,
  onAskAI,
  onViewDetails
}) => {
  return (
    <div className="space-y-6">
      {/* Category Pills Header */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        {CATEGORIES.map(cat => (
          <button
            key={cat}
            onClick={() => onSelectCategory && onSelectCategory(cat)}
            className={`px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all cursor-pointer ${
              selectedCategory === cat
                ? 'bg-amber-500 text-gray-950 shadow-md shadow-amber-500/20'
                : 'bg-gray-800/80 hover:bg-gray-750 text-gray-300 border border-gray-700/60'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Grid Results */}
      {products.length === 0 ? (
        <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-12 text-center">
          <ShoppingBag className="w-12 h-12 text-gray-600 mx-auto mb-3" />
          <h4 className="text-gray-300 font-semibold text-lg">No products found</h4>
          <p className="text-gray-500 text-sm mt-1">
            Try asking with a different voice query or select a category above.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {products.map(product => {
            const isSelected = compareList.some(p => p.id === product.id);
            return (
              <ProductCard
                key={product.id}
                product={product}
                isSelectedForCompare={isSelected}
                onCompareToggle={onCompareToggle}
                onAskAI={onAskAI}
                onViewDetails={onViewDetails}
              />
            );
          })}
        </div>
      )}
    </div>
  );
};
