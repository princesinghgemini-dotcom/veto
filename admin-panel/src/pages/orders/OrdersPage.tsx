import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { ordersApi } from '../../api/orders';
import { DataTable } from '../../components/common/DataTable';
import type { Order } from '../../types';

export function OrdersPage() {
    const navigate = useNavigate();
    const [statusFilter, setStatusFilter] = useState('');

    const { data: orders = [], isLoading } = useQuery({
        queryKey: ['orders', statusFilter],
        queryFn: () => ordersApi.list(statusFilter ? { status: statusFilter } : undefined).then((r) => r.data),
    });

    const getStatusClass = (status: string) => {
        switch (status) {
            case 'pending': return 'pending';
            case 'accepted':
            case 'fulfilled': return 'active';
            case 'rejected':
            case 'cancelled': return 'inactive';
            default: return '';
        }
    };

    const columns = [
        { key: 'id', header: 'Order ID', render: (o: Order) => o.id.slice(0, 8) + '...' },
        { key: 'farmer_id', header: 'Farmer', render: (o: Order) => o.farmer_id?.slice(0, 8) || '-' },
        { key: 'retailer_id', header: 'Retailer', render: (o: Order) => o.retailer_id?.slice(0, 8) || '-' },
        {
            key: 'status', header: 'Status', render: (o: Order) => (
                <span className={`status-badge ${getStatusClass(o.status)}`}>{o.status}</span>
            )
        },
        { key: 'total_amount', header: 'Total', render: (o: Order) => `₹${o.total_amount}` },
        { key: 'created_at', header: 'Date', render: (o: Order) => new Date(o.created_at).toLocaleDateString() },
        {
            key: 'actions', header: 'Actions', render: (o: Order) => (
                <button className="btn btn-secondary btn-sm" onClick={() => navigate(`/orders/${o.id}`)}>View</button>
            ),
        },
    ];

    return (
        <div>
            <div className="page-header">
                <h2>Orders</h2>
                <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} style={{ padding: '8px', borderRadius: '4px' }}>
                    <option value="">All Statuses</option>
                    <option value="pending">Pending</option>
                    <option value="accepted">Accepted</option>
                    <option value="fulfilled">Fulfilled</option>
                    <option value="rejected">Rejected</option>
                    <option value="cancelled">Cancelled</option>
                </select>
            </div>

            <DataTable columns={columns} data={orders} loading={isLoading} />
        </div>
    );
}
