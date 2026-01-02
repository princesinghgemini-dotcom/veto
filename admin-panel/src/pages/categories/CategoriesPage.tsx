import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { categoriesApi } from '../../api/categories';
import { DataTable } from '../../components/common/DataTable';
import { Modal } from '../../components/common/Modal';
import type { ProductCategory } from '../../types';

export function CategoriesPage() {
    const queryClient = useQueryClient();
    const [modalOpen, setModalOpen] = useState(false);
    const [editing, setEditing] = useState<ProductCategory | null>(null);
    const [formData, setFormData] = useState({ name: '', description: '', parent_id: '' });

    const { data: categories = [], isLoading } = useQuery({
        queryKey: ['categories'],
        queryFn: () => categoriesApi.list().then((r) => r.data),
    });

    const createMutation = useMutation({
        mutationFn: categoriesApi.create,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['categories'] });
            closeModal();
        },
    });

    const updateMutation = useMutation({
        mutationFn: ({ id, data }: { id: string; data: Partial<ProductCategory> }) =>
            categoriesApi.update(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['categories'] });
            closeModal();
        },
    });

    const openCreate = () => {
        setEditing(null);
        setFormData({ name: '', description: '', parent_id: '' });
        setModalOpen(true);
    };

    const openEdit = (category: ProductCategory) => {
        setEditing(category);
        setFormData({
            name: category.name,
            description: category.description || '',
            parent_id: category.parent_id || '',
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
            name: formData.name,
            description: formData.description || undefined,
            parent_id: formData.parent_id || undefined,
        };
        if (editing) {
            updateMutation.mutate({ id: editing.id, data });
        } else {
            createMutation.mutate(data);
        }
    };

    const columns = [
        { key: 'name', header: 'Name' },
        { key: 'description', header: 'Description' },
        {
            key: 'parent_id',
            header: 'Parent',
            render: (item: ProductCategory) =>
                categories.find((c) => c.id === item.parent_id)?.name || '-',
        },
        {
            key: 'actions',
            header: 'Actions',
            render: (item: ProductCategory) => (
                <button className="btn btn-secondary btn-sm" onClick={() => openEdit(item)}>
                    Edit
                </button>
            ),
        },
    ];

    return (
        <div>
            <div className="page-header">
                <h2>Product Categories</h2>
                <button className="btn btn-primary" onClick={openCreate}>
                    Add Category
                </button>
            </div>

            <DataTable columns={columns} data={categories} loading={isLoading} />

            <Modal isOpen={modalOpen} onClose={closeModal} title={editing ? 'Edit Category' : 'New Category'}>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Name</label>
                        <input
                            type="text"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label>Description</label>
                        <textarea
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        />
                    </div>
                    <div className="form-group">
                        <label>Parent Category</label>
                        <select
                            value={formData.parent_id}
                            onChange={(e) => setFormData({ ...formData, parent_id: e.target.value })}
                        >
                            <option value="">None</option>
                            {categories
                                .filter((c) => c.id !== editing?.id)
                                .map((c) => (
                                    <option key={c.id} value={c.id}>
                                        {c.name}
                                    </option>
                                ))}
                        </select>
                    </div>
                    <div className="form-actions">
                        <button type="button" className="btn btn-secondary" onClick={closeModal}>
                            Cancel
                        </button>
                        <button type="submit" className="btn btn-primary">
                            {editing ? 'Update' : 'Create'}
                        </button>
                    </div>
                </form>
            </Modal>
        </div>
    );
}
