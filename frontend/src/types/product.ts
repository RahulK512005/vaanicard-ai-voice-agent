export interface Product {
  id: string;
  name: string;
  category: string;
  brand: string;
  description: string;
  price: number;
  original_price: number;
  discount_percentage: number;
  color: string;
  sizes: (number | string)[];
  rating: number;
  stock: number;
  features: string[];
  tags: string[];
}

export interface PriceCalculation {
  product_id: string;
  product_name: string;
  original_mrp: number;
  base_price: number;
  unit_discount_amount: number;
  unit_discount_percentage: number;
  quantity: number;
  subtotal: number;
  coupon_code?: string;
  coupon_discount: number;
  coupon_applied_success: boolean;
  coupon_message?: string;
  gst_amount: number;
  final_payable: number;
  currency: string;
}

export interface ComparisonData {
  products: Product[];
  price_diff: number;
  cheaper: string;
  higher_rated: string;
}
