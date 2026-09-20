import React, { useState } from 'react';
import { X, Star, Check, Tag, ShieldCheck, Truck, RefreshCw } from 'lucide-react';
import { Product, PriceCalculation } from '../types/product';
import { calculateAuthoritativePrice } from '../services/api';

interface ProductDetailsModalProps {
  product: Product | null;
  onClose: () => void;
  onAskAIAboutThis: (product: Product) => void;
}

export const ProductDetailsModal: React.FC<ProductDetailsModalProps> = ({
  product,
  onClose,
  onAskAIAboutThis
}) => {
  if (!product) return null;

  const [couponCode, setCouponCode] = useState<string>('VAANI100');
  const [pricingCalc, setPricingCalc] = useState<PriceCalculation | null>(null);
  const [isApplying, setIsApplying] = useState<boolean>(false);
  const [selectedSize, setSelectedSize] = useState<any>(product.sizes[0] || 'Default');

  const handleApplyCoupon = async () => {
    setIsApplying(true);
    try {
      const calc = await calculateAuthoritativePrice(product.id, 1, couponCode);
      setPricingCalc(calc);
    } catch (err) {
      console.warn('Coupon calculation failed:', err);
    } finally {
      setIsApplying(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-gray-900 border border-gray-800 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl p-6 relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Brand & Category */}
        <div className="flex items-center gap-2 text-xs font-semibold text-amber-400 uppercase tracking-wider mb-1">
          <span>{product.brand}</span>
          <span>•</span>
          <span>{product.category}</span>
        </div>

        <h2 className="text-2xl font-bold text-white mb-2">{product.name}</h2>

        {/* Rating and Reviews */}
        <div className="flex items-center gap-2 mb-4">
          <div className="flex items-center gap-1 bg-amber-400/10 text-amber-400 px-2 py-0.5 rounded text-xs font-bold border border-amber-400/20">
            <Star className="w-3.5 h-3.5 fill-current" />
            <span>{product.rating} / 5</span>
          </div>
          <span className="text-xs text-gray-400">Verified Catalog Item</span>
          <span className="text-xs text-emerald-400 font-semibold">• {product.stock} in stock</span>
        </div>

        {/* Pricing Banner */}
        <div className="p-4 rounded-xl bg-gray-800/60 border border-gray-700/60 mb-5 flex flex-wrap items-baseline justify-between gap-3">
          <div>
            <span className="text-xs text-gray-400 block">Current Price (Incl. GST)</span>
            <div className="flex items-baseline gap-2 mt-0.5">
              <span className="text-3xl font-black text-white">
                ₹{(pricingCalc ? pricingCalc.final_payable : product.price).toLocaleString('en-IN')}
              </span>
              <span className="text-sm text-gray-500 line-through">
                ₹{product.original_price.toLocaleString('en-IN')}
              </span>
              <span className="text-xs bg-amber-500 text-gray-950 font-bold px-2 py-0.5 rounded shadow">
                {product.discount_percentage}% OFF
              </span>
            </div>
          </div>

          {/* Coupon Tester */}
          <div className="space-y-1">
            <span className="text-xs text-gray-400 block font-medium">Test Authoritative Coupon:</span>
            <div className="flex items-center gap-1.5">
              <input
                type="text"
                value={couponCode}
                onChange={e => setCouponCode(e.target.value.toUpperCase())}
                placeholder="e.g. VAANI100"
                className="bg-gray-950 border border-gray-700 rounded-lg px-2.5 py-1 text-xs text-white uppercase focus:outline-none focus:border-amber-500 w-28"
              />
              <button
                onClick={handleApplyCoupon}
                disabled={isApplying}
                className="px-3 py-1 bg-amber-500 hover:bg-amber-400 text-gray-950 text-xs font-bold rounded-lg transition-colors cursor-pointer"
              >
                {isApplying ? 'Applying...' : 'Apply'}
              </button>
            </div>
            {pricingCalc?.coupon_message && (
              <p className={`text-[11px] ${pricingCalc.coupon_applied_success ? 'text-emerald-400' : 'text-rose-400'}`}>
                {pricingCalc.coupon_message}
              </p>
            )}
          </div>
        </div>

        {/* Description */}
        <div className="mb-5">
          <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider mb-1.5">Description</h4>
          <p className="text-sm text-gray-300 leading-relaxed">{product.description}</p>
        </div>

        {/* Sizes */}
        {product.sizes && product.sizes.length > 0 && (
          <div className="mb-5">
            <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider mb-2">Available Sizes</h4>
            <div className="flex flex-wrap gap-2">
              {product.sizes.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedSize(s)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold border cursor-pointer ${
                    selectedSize === s
                      ? 'bg-amber-500 text-gray-950 border-amber-500 font-bold'
                      : 'bg-gray-800 text-gray-300 border-gray-700 hover:bg-gray-750'
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Key Features */}
        {product.features && product.features.length > 0 && (
          <div className="mb-6">
            <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider mb-2">Verified Specifications</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {product.features.map((feat, idx) => (
                <div key={idx} className="flex items-start gap-2 bg-gray-800/40 p-2.5 rounded-lg border border-gray-800 text-xs text-gray-300">
                  <Check className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                  <span>{feat}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Trust Badges */}
        <div className="grid grid-cols-3 gap-2 py-3 border-t border-b border-gray-800 mb-6 text-center text-xs text-gray-400">
          <div className="flex flex-col items-center gap-1">
            <Truck className="w-4 h-4 text-amber-400" />
            <span>Fast Dispatch across India</span>
          </div>
          <div className="flex flex-col items-center gap-1">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>100% Genuine Guarantee</span>
          </div>
          <div className="flex flex-col items-center gap-1">
            <RefreshCw className="w-4 h-4 text-blue-400" />
            <span>7-Day Easy Returns</span>
          </div>
        </div>

        {/* Footer actions */}
        <div className="flex items-center justify-between gap-3">
          <button
            onClick={() => {
              onAskAIAboutThis(product);
              onClose();
            }}
            className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-orange-600 to-amber-500 hover:from-orange-500 hover:to-amber-400 text-white font-bold text-sm shadow-lg shadow-orange-500/20 transition-all cursor-pointer text-center"
          >
            Ask AI about this product
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm font-medium transition-colors cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
