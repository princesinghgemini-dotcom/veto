import apiClient from './client';
import type { Product, ProductVariant } from '../types';

export const productsApi = {
    list: (categoryId?: string) =>
        apiClient.get<Product[]>('/products', {
            params: categoryId ? { category_id: categoryId } : undefined,
        }),

    create: (data: Omit<Product, 'id' | 'created_at'>) =>
        apiClient.post<Product>('/products', data),

    update: (id: string, data: Partial<Product>) =>
        apiClient.patch<Product>(`/products/${id}`, data),

    // Variants
    listVariants: (productId: string) =>
        apiClient.get<ProductVariant[]>(`/products/${productId}/variants`),

    createVariant: (productId: string, data: Omit<ProductVariant, 'id' | 'product_id' | 'created_at'>) =>
        apiClient.post<ProductVariant>(`/products/${productId}/variants`, data),

    updateVariant: (variantId: string, data: Partial<ProductVariant>) =>
        apiClient.patch<ProductVariant>(`/products/variants/${variantId}`, data),
};
