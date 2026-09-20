import { Product, PriceCalculation } from '../types/product';
import { ChatResponse } from '../types/conversation';
import { fallbackProducts } from '../data/fallbackProducts';

// Auto-detect production deployment (Vercel) vs local development
const isLocalhost =
  typeof window !== 'undefined' &&
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

const DEFAULT_REMOTE_API = 'https://vaanicard-ai-voice-agent.onrender.com';
const DEFAULT_LOCAL_API = 'http://localhost:8000';

const rawApiUrl = import.meta.env.VITE_API_URL || (isLocalhost ? DEFAULT_LOCAL_API : DEFAULT_REMOTE_API);
// Ensure no trailing slash so URLs never have double slashes
export const API_BASE_URL = rawApiUrl.replace(/\/+$/, '');

export async function checkHealth() {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) throw new Error('Backend offline');
  return res.json();
}

export async function sendChatMessage(
  query: string,
  sessionId?: string,
  contextProductId?: string,
  languageHint?: string
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      session_id: sessionId,
      context_product_id: contextProductId,
      language_hint: languageHint,
      voice_input: true
    })
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Chat API error: ${errorText}`);
  }
  return res.json();
}

export async function fetchProducts(category?: string, limit: number = 20): Promise<Product[]> {
  try {
    const url = new URL(`${API_BASE_URL}/api/products`);
    if (category && category !== 'All') {
      url.searchParams.set('category', category);
    }
    url.searchParams.set('limit', limit.toString());

    // 8-second timeout for serverless / sleeping Render backend
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 8000);

    const res = await fetch(url.toString(), { signal: controller.signal });
    clearTimeout(timeoutId);

    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    const data = await res.json();
    if (Array.isArray(data) && data.length > 0) {
      return data;
    }
    throw new Error('Empty product list from API');
  } catch (err) {
    console.warn('Backend fetch failed or timed out, using fallback catalog:', err);
    // Instant fallback filtering from local verified catalog
    if (category && category !== 'All') {
      return fallbackProducts.filter(
        p => p.category.toLowerCase().includes(category.toLowerCase())
      ).slice(0, limit);
    }
    return fallbackProducts.slice(0, limit);
  }
}

export async function fetchProductById(id: string): Promise<Product> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/products/${id}`);
    if (!res.ok) throw new Error(`Product ${id} not found`);
    return await res.json();
  } catch (err) {
    const found = fallbackProducts.find(p => p.id === id);
    if (found) return found;
    throw err;
  }
}

export async function calculateAuthoritativePrice(
  productId: string,
  quantity: number = 1,
  couponCode?: string
): Promise<PriceCalculation> {
  const res = await fetch(`${API_BASE_URL}/api/calculate-price`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      product_id: productId,
      quantity,
      coupon_code: couponCode
    })
  });
  if (!res.ok) throw new Error('Price calculation failed');
  return res.json();
}

export async function compareProductsApi(productIds: string[]) {
  const res = await fetch(`${API_BASE_URL}/api/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_ids: productIds })
  });
  if (!res.ok) throw new Error('Comparison failed');
  return res.json();
}
