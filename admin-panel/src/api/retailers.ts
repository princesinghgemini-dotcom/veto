import apiClient from './client';
import type { Retailer, RetailerProduct } from '../types';

export const retailersApi = {
    list: () => apiClient.get<Retailer[]>('/retailers'),

    create: (data: Omit<Retailer, 'id' | 'created_at'>) =>
        apiClient.post<Retailer>('/retailers', data),

    update: (id: string, data: Partial<Retailer>) =>
        apiClient.patch<Retailer>(`/retailers/${id}`, data),

    // Retailer Products
    listProducts: (retailerId: string) =>
        apiClient.get<RetailerProduct[]>(`/retailers/${retailerId}/products`),

    addProduct: (retailerId: string, data: Omit<RetailerProduct, 'id' | 'retailer_id'>) =>
        apiClient.post<RetailerProduct>(`/retailers/${retailerId}/products`, data),

    updateProduct: (mappingId: string, data: Partial<RetailerProduct>) =>
        apiClient.patch<RetailerProduct>(`/retailer-products/${mappingId}`, data),
};
