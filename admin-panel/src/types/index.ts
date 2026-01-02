// Entity types matching backend schemas

export interface ProductCategory {
    id: string;
    name: string;
    description?: string;
    parent_id?: string;
    created_at: string;
}

export interface Product {
    id: string;
    category_id?: string;
    name: string;
    description?: string;
    manufacturer?: string;
    is_active: boolean;
    created_at: string;
}

export interface ProductVariant {
    id: string;
    product_id: string;
    sku: string;
    name?: string;
    unit_size?: string;
    unit_type?: string;
    base_price?: number;
    is_active: boolean;
    created_at: string;
}

export interface Retailer {
    id: string;
    name: string;
    phone?: string;
    email?: string;
    address?: string;
    location_lat?: number;
    location_lng?: number;
    is_active: boolean;
    created_at: string;
}

export interface RetailerProduct {
    id: string;
    retailer_id: string;
    product_variant_id: string;
    price: number;
    stock_quantity: number;
    is_available: boolean;
}

export interface Order {
    id: string;
    farmer_id?: string;
    retailer_id?: string;
    diagnosis_case_id?: string;
    source_type?: string;
    status: string;
    total_amount: number;
    delivery_address?: string;
    notes?: string;
    created_at: string;
}

export interface OrderItem {
    id: string;
    product_variant_id?: string;
    quantity: number;
    unit_price: number;
}

export interface OrderDetail extends Order {
    items: OrderItem[];
}
