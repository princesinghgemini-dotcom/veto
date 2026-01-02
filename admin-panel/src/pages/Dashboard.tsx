export function Dashboard() {
    return (
        <div>
            <h2>Dashboard</h2>
            <p style={{ color: '#666', marginTop: '16px' }}>
                Welcome to the Cattle Disease Diagnosis Admin Panel.
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginTop: '24px' }}>
                <div style={{ background: 'white', padding: '24px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                    <h3>Categories</h3>
                    <p style={{ color: '#666', marginTop: '8px' }}>Manage product categories</p>
                </div>
                <div style={{ background: 'white', padding: '24px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                    <h3>Products</h3>
                    <p style={{ color: '#666', marginTop: '8px' }}>Manage products and variants</p>
                </div>
                <div style={{ background: 'white', padding: '24px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                    <h3>Retailers</h3>
                    <p style={{ color: '#666', marginTop: '8px' }}>Manage retailer network</p>
                </div>
            </div>
        </div>
    );
}
