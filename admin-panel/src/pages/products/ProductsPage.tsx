import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { productsApi } from '../../api/products';
import { categoriesApi } from '../../api/categories';
import { DataTable } from '../../components/common/DataTable';
import { Modal } from '../../components/common/Modal';
import { StatusBadge } from '../../components/common/StatusBadge';
import type { Product, ProductVariant, ProductCategory } from '../../types';

export function ProductsPage() {
    const queryClient = useQueryClient();
    const [productModalOpen, setProductModalOpen] = useState(false);
    const [variantModalOpen, setVariantModalOpen] = useState(false);
    const [editingProduct, setEditingProduct] = useState<Product | null>(null);
    const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
    const [editingVariant, setEditingVariant] = useState<ProductVariant | null>(null);

    const [productForm, setProductForm] = useState({
        name: '', description: '', manufacturer: '', category_id: '', is_active: true
    });

    const [variantForm, setVariantForm] = useState({
        sku: '', name: '', unit_size: '', unit_type: '', base_price: '', is_active: true
    });

    const { data: products = [], isLoading } = useQuery({
        queryKey: ['products'],
        queryFn: () => productsApi.list().then((r) => r.data),
    });

    const { data: categories = [] } = useQuery({
        queryKey: ['categories'],
        queryFn: () => categoriesApi.list().then((r) => r.data),
    });

    const { data: variants = [] } = useQuery({
        queryKey: ['variants', selectedProduct?.id],
        queryFn: () => productsApi.listVariants(selectedProduct!.id).then((r) => r.data),
        enabled: !!selectedProduct,
    });

    const createProductMutation = useMutation({
        mutationFn: productsApi.create,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['products'] });
            setProductModalOpen(false);
        },
    });

    const updateProductMutation = useMutation({
        mutationFn: ({ id, data }: { id: string; data: Partial<Product> }) =>
            productsApi.update(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['products'] });
            setProductModalOpen(false);
        },
    });

    const createVariantMutation = useMutation({
        mutationFn: ({ productId, data }: { productId: string; data: Omit<ProductVariant, 'id' | 'product_id' | 'created_at'> }) =>
            productsApi.createVariant(productId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['variants', selectedProduct?.id] });
            setVariantModalOpen(false);
        },
    });

    const updateVariantMutation = useMutation({
        mutationFn: ({ id, data }: { id: string; data: Partial<ProductVariant> }) =>
            productsApi.updateVariant(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['variants', selectedProduct?.id] });
            setVariantModalOpen(false);
        },
    });

    const openCreateProduct = () => {
        setEditingProduct(null);
        setProductForm({ name: '', description: '', manufacturer: '', category_id: '', is_active: true });
        setProductModalOpen(true);
    };

    const openEditProduct = (product: Product) => {
        setEditingProduct(product);
        setProductForm({
            name: product.name,
            description: product.description || '',
            manufacturer: product.manufacturer || '',
            category_id: product.category_id || '',
            is_active: product.is_active,
        });
        setProductModalOpen(true);
    };

    const handleProductSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const data = {
            name: productForm.name,
            description: productForm.description || undefined,
            manufacturer: productForm.manufacturer || undefined,
            category_id: productForm.category_id || undefined,
            is_active: productForm.is_active,
        };
        if (editingProduct) {
            updateProductMutation.mutate({ id: editingProduct.id, data });
        } else {
            createProductMutation.mutate(data as Product);
        }
    };

    const openCreateVariant = () => {
        setEditingVariant(null);
        setVariantForm({ sku: '', name: '', unit_size: '', unit_type: '', base_price: '', is_active: true });
        setVariantModalOpen(true);
    };

    const openEditVariant = (variant: ProductVariant) => {
        setEditingVariant(variant);
        setVariantForm({
            sku: variant.sku,
            name: variant.name || '',
            unit_size: variant.unit_size || '',
            unit_type: variant.unit_type || '',
            base_price: variant.base_price?.toString() || '',
            is_active: variant.is_active,
        });
        setVariantModalOpen(true);
    };

    const handleVariantSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const data = {
            sku: variantForm.sku,
            name: variantForm.name || undefined,
            unit_size: variantForm.unit_size || undefined,
            unit_type: variantForm.unit_type || undefined,
            base_price: variantForm.base_price ? parseFloat(variantForm.base_price) : undefined,
            is_active: variantForm.is_active,
        };
        if (editingVariant) {
            updateVariantMutation.mutate({ id: editingVariant.id, data });
        } else {
            createVariantMutation.mutate({ productId: selectedProduct!.id, data });
        }
    };

    const getCategoryName = (categoryId?: string) =>
        categories.find((c: ProductCategory) => c.id === categoryId)?.name || '-';

    const productColumns = [
        { key: 'name', header: 'Name' },
        { key: 'category_id', header: 'Category', render: (p: Product) => getCategoryName(p.category_id) },
        { key: 'manufacturer', header: 'Manufacturer' },
        { key: 'is_active', header: 'Status', render: (p: Product) => <StatusBadge status={p.is_active} /> },
        {
            key: 'actions', header: 'Actions', render: (p: Product) => (
                <div style={{ display: 'flex', gap: '8px' }}>
                    <button className="btn btn-secondary btn-sm" onClick={() => setSelectedProduct(p)}>Variants</button>
                    <button className="btn btn-secondary btn-sm" onClick={() => openEditProduct(p)}>Edit</button>
                </div>
            ),
        },
    ];

    const variantColumns = [
        { key: 'sku', header: 'SKU' },
        { key: 'name', header: 'Name' },
        { key: 'unit_size', header: 'Size' },
        { key: 'base_price', header: 'Base Price', render: (v: ProductVariant) => v.base_price ? `₹${v.base_price}` : '-' },
        { key: 'is_active', header: 'Status', render: (v: ProductVariant) => <StatusBadge status={v.is_active} /> },
        {
            key: 'actions', header: 'Actions', render: (v: ProductVariant) => (
                <button className="btn btn-secondary btn-sm" onClick={() => openEditVariant(v)}>Edit</button>
            ),
        },
    ];

    return (
        <div>
            <div className="page-header">
                <h2>{selectedProduct ? `Variants: ${selectedProduct.name}` : 'Products'}</h2>
                {selectedProduct ? (
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <button className="btn btn-secondary" onClick={() => setSelectedProduct(null)}>Back</button>
                        <button className="btn btn-primary" onClick={openCreateVariant}>Add Variant</button>
                    </div>
                ) : (
                    <button className="btn btn-primary" onClick={openCreateProduct}>Add Product</button>
                )}
            </div>

            {selectedProduct ? (
                <DataTable columns={variantColumns} data={variants} />
            ) : (
                <DataTable columns={productColumns} data={products} loading={isLoading} />
            )}

            {/* Product Modal */}
            <Modal isOpen={productModalOpen} onClose={() => setProductModalOpen(false)} title={editingProduct ? 'Edit Product' : 'New Product'}>
                <form onSubmit={handleProductSubmit}>
                    <div className="form-group">
                        <label>Name</label>
                        <input type="text" value={productForm.name} onChange={(e) => setProductForm({ ...productForm, name: e.target.value })} required />
                    </div>
                    <div className="form-group">
                        <label>Category</label>
                        <select value={productForm.category_id} onChange={(e) => setProductForm({ ...productForm, category_id: e.target.value })}>
                            <option value="">None</option>
                            {categories.map((c: ProductCategory) => <option key={c.id} value={c.id}>{c.name}</option>)}
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Manufacturer</label>
                        <input type="text" value={productForm.manufacturer} onChange={(e) => setProductForm({ ...productForm, manufacturer: e.target.value })} />
                    </div>
                    <div className="form-group">
                        <label><input type="checkbox" checked={productForm.is_active} onChange={(e) => setProductForm({ ...productForm, is_active: e.target.checked })} /> Active</label>
                    </div>
                    <div className="form-actions">
                        <button type="button" className="btn btn-secondary" onClick={() => setProductModalOpen(false)}>Cancel</button>
                        <button type="submit" className="btn btn-primary">{editingProduct ? 'Update' : 'Create'}</button>
                    </div>
                </form>
            </Modal>

            {/* Variant Modal */}
            <Modal isOpen={variantModalOpen} onClose={() => setVariantModalOpen(false)} title={editingVariant ? 'Edit Variant' : 'New Variant'}>
                <form onSubmit={handleVariantSubmit}>
                    <div className="form-group">
                        <label>SKU</label>
                        <input type="text" value={variantForm.sku} onChange={(e) => setVariantForm({ ...variantForm, sku: e.target.value })} required />
                    </div>
                    <div className="form-group">
                        <label>Name</label>
                        <input type="text" value={variantForm.name} onChange={(e) => setVariantForm({ ...variantForm, name: e.target.value })} />
                    </div>
                    <div className="form-group">
                        <label>Unit Size</label>
                        <input type="text" value={variantForm.unit_size} onChange={(e) => setVariantForm({ ...variantForm, unit_size: e.target.value })} placeholder="e.g. 500ml" />
                    </div>
                    <div className="form-group">
                        <label>Base Price</label>
                        <input type="number" step="0.01" value={variantForm.base_price} onChange={(e) => setVariantForm({ ...variantForm, base_price: e.target.value })} />
                    </div>
                    <div className="form-group">
                        <label><input type="checkbox" checked={variantForm.is_active} onChange={(e) => setVariantForm({ ...variantForm, is_active: e.target.checked })} /> Active</label>
                    </div>
                    <div className="form-actions">
                        <button type="button" className="btn btn-secondary" onClick={() => setVariantModalOpen(false)}>Cancel</button>
                        <button type="submit" className="btn btn-primary">{editingVariant ? 'Update' : 'Create'}</button>
                    </div>
                </form>
            </Modal>
        </div>
    );
}
