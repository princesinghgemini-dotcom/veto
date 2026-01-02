import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppLayout } from './components/layout/AppLayout';
import { Dashboard } from './pages/Dashboard';
import { CategoriesPage } from './pages/categories/CategoriesPage';
import { ProductsPage } from './pages/products/ProductsPage';
import { RetailersPage } from './pages/retailers/RetailersPage';
import { RetailerProductsPage } from './pages/retailer-products/RetailerProductsPage';
import { OrdersPage } from './pages/orders/OrdersPage';
import { OrderDetailPage } from './pages/orders/OrderDetailPage';

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 30000,
            retry: 1,
        },
    },
});

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <BrowserRouter>
                <Routes>
                    <Route element={<AppLayout />}>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/categories" element={<CategoriesPage />} />
                        <Route path="/products" element={<ProductsPage />} />
                        <Route path="/retailers" element={<RetailersPage />} />
                        <Route path="/retailer-products" element={<RetailerProductsPage />} />
                        <Route path="/orders" element={<OrdersPage />} />
                        <Route path="/orders/:id" element={<OrderDetailPage />} />
                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Route>
                </Routes>
            </BrowserRouter>
        </QueryClientProvider>
    );
}

export default App;
