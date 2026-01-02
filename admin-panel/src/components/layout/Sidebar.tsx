import { NavLink } from 'react-router-dom';

export function Sidebar() {
    return (
        <aside className="sidebar">
            <h1>Admin Panel</h1>
            <nav>
                <NavLink to="/categories">Categories</NavLink>
                <NavLink to="/products">Products</NavLink>
                <NavLink to="/retailers">Retailers</NavLink>
                <NavLink to="/retailer-products">Product Mappings</NavLink>
                <NavLink to="/orders">Orders</NavLink>
            </nav>
        </aside>
    );
}
