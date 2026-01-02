import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { retailersApi } from '../../api/retailers';
import { DataTable } from '../../components/common/DataTable';
import { Modal } from '../../components/common/Modal';
import { StatusBadge } from '../../components/common/StatusBadge';
import type { Retailer } from '../../types';

export function RetailersPage() {
    const queryClient = useQueryClient();
    const [modalOpen, setModalOpen] = useState(false);
    const [editing, setEditing] = useState<Retailer | null>(null);
    const [formData, setFormData] = useState({
        name: '', phone: '', email: '', address: '',
        location_lat: '', location_lng: '', is_active: true
    });

    const { data: retailers = [], isLoading } = useQuery({
        queryKey: ['retailers'],
        queryFn: () => retailersApi.list().then((r) => r.data),
    });

    const createMutation = useMutation({
        mutationFn: retailersApi.create,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['retailers'] });
            closeModal();
        },
    });

    const updateMutation = useMutation({
        mutationFn: ({ id, data }: { id: string; data: Partial<Retailer> }) =>
            retailersApi.update(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['retailers'] });
            closeModal();
        },
    });

    const openCreate = () => {
        setEditing(null);
        setFormData({ name: '', phone: '', email: '', address: '', location_lat: '', location_lng: '', is_active: true });
        setModalOpen(true);
    };

    const openEdit = (retailer: Retailer) => {
        setEditing(retailer);
        setFormData({
            name: retailer.name,
            phone: retailer.phone || '',
            email: retailer.email || '',
            address: retailer.address || '',
            location_lat: retailer.location_lat?.toString() || '',
            location_lng: retailer.location_lng?.toString() || '',
            is_active: retailer.is_active,
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
            phone: formData.phone || undefined,
            email: formData.email || undefined,
            address: formData.address || undefined,
            location_lat: formData.location_lat ? parseFloat(formData.location_lat) : undefined,
            location_lng: formData.location_lng ? parseFloat(formData.location_lng) : undefined,
            is_active: formData.is_active,
        };
        if (editing) {
            updateMutation.mutate({ id: editing.id, data });
        } else {
            createMutation.mutate(data as Retailer);
        }
    };

    const columns = [
        { key: 'name', header: 'Name' },
        { key: 'phone', header: 'Phone' },
        { key: 'email', header: 'Email' },
        { key: 'address', header: 'Address' },
        { key: 'is_active', header: 'Status', render: (r: Retailer) => <StatusBadge status={r.is_active} /> },
        {
            key: 'actions', header: 'Actions', render: (r: Retailer) => (
                <button className="btn btn-secondary btn-sm" onClick={() => openEdit(r)}>Edit</button>
            ),
        },
    ];

    return (
        <div>
            <div className="page-header">
                <h2>Retailers</h2>
                <button className="btn btn-primary" onClick={openCreate}>Add Retailer</button>
            </div>

            <DataTable columns={columns} data={retailers} loading={isLoading} />

            <Modal isOpen={modalOpen} onClose={closeModal} title={editing ? 'Edit Retailer' : 'New Retailer'}>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Name</label>
                        <input type="text" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} required />
                    </div>
                    <div className="form-group">
                        <label>Phone</label>
                        <input type="text" value={formData.phone} onChange={(e) => setFormData({ ...formData, phone: e.target.value })} />
                    </div>
                    <div className="form-group">
                        <label>Email</label>
                        <input type="email" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} />
                    </div>
                    <div className="form-group">
                        <label>Address</label>
                        <textarea value={formData.address} onChange={(e) => setFormData({ ...formData, address: e.target.value })} />
                    </div>
                    <div style={{ display: 'flex', gap: '16px' }}>
                        <div className="form-group" style={{ flex: 1 }}>
                            <label>Latitude</label>
                            <input type="number" step="any" value={formData.location_lat} onChange={(e) => setFormData({ ...formData, location_lat: e.target.value })} />
                        </div>
                        <div className="form-group" style={{ flex: 1 }}>
                            <label>Longitude</label>
                            <input type="number" step="any" value={formData.location_lng} onChange={(e) => setFormData({ ...formData, location_lng: e.target.value })} />
                        </div>
                    </div>
                    <div className="form-group">
                        <label><input type="checkbox" checked={formData.is_active} onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })} /> Active</label>
                    </div>
                    <div className="form-actions">
                        <button type="button" className="btn btn-secondary" onClick={closeModal}>Cancel</button>
                        <button type="submit" className="btn btn-primary">{editing ? 'Update' : 'Create'}</button>
                    </div>
                </form>
            </Modal>
        </div>
    );
}
