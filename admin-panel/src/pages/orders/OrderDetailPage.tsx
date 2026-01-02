import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ordersApi } from '../../api/orders';
import { DataTable } from '../../components/common/DataTable';
import type { OrderItem } from '../../types';

export function OrderDetailPage() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();

    const { data: order, isLoading } = useQuery({
        queryKey: ['order', id],
        queryFn: () => ordersApi.get(id!).then((r) => r.data),
        enabled: !!id,
    });

    if (isLoading) return <div className="loading">Loading...</div>;
    if (!order) return <div className="error">Order not found</div>;

    const itemColumns = [
        { key: 'product_variant_id', header: 'Product Variant', render: (item: OrderItem) => item.product_variant_id?.slice(0, 8) || '-' },
        { key: 'quantity', header: 'Quantity' },
        { key: 'unit_price', header: 'Unit Price', render: (item: OrderItem) => `₹${item.unit_price}` },
        { key: 'total', header: 'Total', render: (item: OrderItem) => `₹${(item.unit_price * item.quantity).toFixed(2)}` },
    ];

    return (
        <div>
            <div className="page-header">
                <h2>Order Details</h2>
                <button className="btn btn-secondary" onClick={() => navigate('/orders')}>Back</button>
            </div>

            <div style={{ background: 'white', padding: '24px', borderRadius: '8px', marginBottom: '24px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                    <div>
                        <strong>Order ID:</strong><br />{order.id}
                    </div>
                    <div>
                        <strong>Status:</strong><br />
                        <span className={`status-badge ${order.status === 'pending' ? 'pending' : order.status === 'fulfilled' ? 'active' : 'inactive'}`}>
                            {order.status}
                        </span>
                    </div>
                    <div>
                        <strong>Total Amount:</strong><br />₹{order.total_amount}
                    </div>
                    <div>
                        <strong>Farmer ID:</strong><br />{order.farmer_id || '-'}
                    </div>
                    <div>
                        <strong>Retailer ID:</strong><br />{order.retailer_id || '-'}
                    </div>
                    <div>
                        <strong>Date:</strong><br />{new Date(order.created_at).toLocaleString()}
                    </div>
                    <div style={{ gridColumn: 'span 3' }}>
                        <strong>Delivery Address:</strong><br />{order.delivery_address || '-'}
                    </div>
                    {order.notes && (
                        <div style={{ gridColumn: 'span 3' }}>
                            <strong>Notes:</strong><br />{order.notes}
                        </div>
                    )}
                </div>
            </div>

            <h3 style={{ marginBottom: '16px' }}>Order Items</h3>
            <DataTable columns={itemColumns} data={order.items || []} />
        </div>
    );
}
