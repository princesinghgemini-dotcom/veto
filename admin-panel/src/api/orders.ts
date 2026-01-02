import apiClient from './client';
import type { Order, OrderDetail } from '../types';

export const ordersApi = {
    list: (params?: { status?: string; retailer_id?: string; farmer_id?: string }) =>
        apiClient.get<Order[]>('/orders', { params }),

    get: (id: string) => apiClient.get<OrderDetail>(`/orders/${id}`),
};
