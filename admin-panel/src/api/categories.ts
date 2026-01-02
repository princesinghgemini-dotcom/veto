import apiClient from './client';
import type { ProductCategory } from '../types';

export const categoriesApi = {
    list: (parentId?: string) =>
        apiClient.get<ProductCategory[]>('/categories', {
            params: parentId ? { parent_id: parentId } : undefined,
        }),

    create: (data: { name: string; description?: string; parent_id?: string }) =>
        apiClient.post<ProductCategory>('/categories', data),

    update: (id: string, data: Partial<ProductCategory>) =>
        apiClient.patch<ProductCategory>(`/categories/${id}`, data),
};
