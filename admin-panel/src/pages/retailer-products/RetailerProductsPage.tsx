import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { retailersApi } from '../../api/retailers';
import { productsApi } from '../../api/products';
import { DataTable } from '../../components/common/DataTable';
import { Modal } from '../../components/common/Modal';
import { StatusBadge } from '../../components/common/StatusBadge';
import type { Retailer, RetailerProduct, ProductVariant } from '../../types';

export function RetailerProductsPage() {
    const queryClient = useQueryClient();
    const [selectedRetailer, setSelectedRetailer] = useState<Retailer | null>(null);
    const [modalOpen, setModalOpen] = useState(false);
    const [editing, setEditing] = useState<RetailerProduct | null>(null);
    const [formData, setFormData] = useState({
        product_variant_id: '', price: '', stock_quantity: '0', is_available: true
    });

    const { data: retailers = [] } = useQuery({
        queryKey: ['retailers'],
        queryFn: () => retailersApi.list().then((r) => r.data),
    });

    const { data: products = [] } = useQuery({
        queryKey: ['all-variants'],
        queryFn: async () => {
            const productsRes = await productsApi.list();
            const allVariants: ProductVariant[] = [];
            for (const product of productsRes.data) {
                const variantsRes = await productsApi.listVariants(product.id);
                allVariants.push(...variantsRes.data);
            }
            return allVariants;
        },
    });

    const { data: mappings = [], isLoading } = useQuery({
        queryKey: ['retailer-products', selectedRetailer?.id],
        queryFn: () => retailersApi.listProducts(selectedRetailer!.id).then((r) => r.data),
        enabled: !!selectedRetailer,
    });

    const addProductMutation = useMutation({
        mutationFn: ({ retailerId, data }: { retailerId: string; data: Omit<RetailerProduct, 'id' | 'retailer_id'> }) =>
            retailersApi.addProduct(retailerId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['retailer-products', selectedRetailer?.id] });
            closeModal();
        },
    });

    const updateProductMutation = useMutation({
        mutationFn: ({ id, data }: { id: string; data: Partial<RetailerProduct> }) =>
            retailersApi.updateProduct(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['retailer-products', selectedRetailer?.id] });
            closeModal();
        },
    });

    const openCreate = () => {
        setEditing(null);
        setFormData({ product_variant_id: '', price: '', stock_quantity: '0', is_available: true });
        setModalOpen(true);
    };

    const openEdit = (mapping: RetailerProduct) => {
        setEditing(mapping);
        setFormData({
            product_variant_id: mapping.product_variant_id,
            price: mapping.price.toString(),
            stock_quantity: mapping.stock_quantity.toString(),
            is_available: mapping.is_available,
        });
        setModalOpen(true);
    };

    const closeModal = () => {
        setModalOpen(false);
        setEditing(null);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const data = {
            product_variant_id: formData.product_variant_id,
            price: parseFloat(formData.price),
            stock_quantity: parseInt(formData.stock_quantity),
            is_available: formData.is_available,
        };
        if (editing) {
            updateProductMutation.mutate({ id: editing.id, data });
        } else {
            addProductMutation.mutate({ retailerId: selectedRetailer!.id, data });
        }
    };

    const getVariantDisplay = (variantId: string) => {
        const variant = products.find((v) => v.id === variantId);
        return variant ? `${variant.sku} - ${variant.name || 'Unnamed'}` : variantId;
    };

    const retailerColumns = [
        { key: 'name', header: 'Retailer Name' },
        { key: 'phone', header: 'Phone' },
        { key: 'is_active', header: 'Status', render: (r: Retailer) => <StatusBadge status={r.is_active} /> },
        {
            key: 'actions', header: 'Actions', render: (r: Retailer) => (
                <button className="btn btn-primary btn-sm" onClick={() => setSelectedRetailer(r)}>Manage Products</button>
            ),
        },
    ];

    const mappingColumns = [
        { key: 'product_variant_id', header: 'Product', render: (m: RetailerProduct) => getVariantDisplay(m.product_variant_id) },
        { key: 'price', header: 'Price', render: (m: RetailerProduct) => `₹${m.price}` },
        { key: 'stock_quantity', header: 'Stock' },
        { key: 'is_available', header: 'Available', render: (m: RetailerProduct) => <StatusBadge status={m.is_available} activeText="Yes" inactiveText="No" /> },
        {
            key: 'actions', header: 'Actions', render: (m: RetailerProduct) => (
                <button className="btn btn-secondary btn-sm" onClick={() => openEdit(m)}>Edit</button>
            ),
        },
    ];

    return (
        <div>
            <div className="page-header">
                <h2>{selectedRetailer ? `Products: ${selectedRetailer.name}` : 'Retailer Product Mappings'}</h2>
                {selectedRetailer && (
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <button className="btn btn-secondary" onClick={() => setSelectedRetailer(null)}>Back</button>
                        <button className="btn btn-primary" onClick={openCreate}>Add Product</button>
                    </div>
                )}
            </div>

            {selectedRetailer ? (
                <DataTable columns={mappingColumns} data={mappings} loading={isLoading} />
            ) : (
                <DataTable columns={retailerColumns} data={retailers} />
            )}

            <Modal isOpen={modalOpen} onClose={closeModal} title={editing ? 'Edit Mapping' : 'Add Product'}>
                <form onSubmit={handleSubmit}>
                    {!editing && (
                        <div className="form-group">
                            <label>Product Variant</label>
                            <select value={formData.product_variant_id} onChange={(e) => setFormData({ ...formData, product_variant_id: e.target.value })} required>
                                <option value="">Select...</option>
                                {products.map((v) => (
                                    <option key={v.id} value={v.id}>{v.sku} - {v.name || 'Unnamed'}</option>
                                ))}
                            </select>
                        </div>
                    )}
                    <div className="form-group">
                        <label>Price</label>
                        <input type="number" step="0.01" value={formData.price} onChange={(e) => setFormData({ ...formData, price: e.target.value })} required />
                    </div>
                    <div className="form-group">
                        <label>Stock Quantity</label>
                        <input type="number" value={formData.stock_quantity} onChange={(e) => setFormData({ ...formData, stock_quantity: e.target.value })} required />
                    </div>
                    <div className="form-group">
                        <label><input type="checkbox" checked={formData.is_available} onChange={(e) => setFormData({ ...formData, is_available: e.target.checked })} /> Available</label>
                    </div>
                    <div className="form-actions">
                        <button type="button" className="btn btn-secondary" onClick={closeModal}>Cancel</button>
                        <button type="submit" className="btn btn-primary">{editing ? 'Update' : 'Add'}</button>
                    </div>
                </form>
            </Modal>
        </div>
    );
}
