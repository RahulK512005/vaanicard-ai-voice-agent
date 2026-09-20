import { Product, PriceCalculation } from '../types/product';
import { ChatResponse } from '../types/conversation';

// Auto-detect production deployment (Vercel) vs local development
const isLocalhost =
  typeof window !== 'undefined' &&
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

const DEFAULT_REMOTE_API = 'https://vaanicard-ai-voice-agent.onrender.com';
const DEFAULT_LOCAL_API = 'http://localhost:8000';

const API_BASE_URL = import.meta.env.VITE_API_URL || (isLocalhost ? DEFAULT_LOCAL_API : DEFAULT_REMOTE_API);

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
  const url = new URL(`${API_BASE_URL}/api/products`);
  if (category) url.searchParams.set('category', category);
  url.searchParams.set('limit', limit.toString());

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error('Failed to fetch products');
  return res.json();
}

export async function fetchProductById(id: string): Promise<Product> {
  const res = await fetch(`${API_BASE_URL}/api/products/${id}`);
  if (!res.ok) throw new Error(`Product ${id} not found`);
  return res.json();
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
