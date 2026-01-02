import axios from 'axios';

let apiUrl = import.meta.env.VITE_API_URL || '/api/admin';
if (apiUrl !== '/api/admin' && !apiUrl.startsWith('http')) {
    apiUrl = `https://${apiUrl}`;
}

const apiClient = axios.create({
    baseURL: apiUrl,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Auth interceptor (stub - add token when auth is implemented)
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('admin_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Error interceptor
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Handle unauthorized
            localStorage.removeItem('admin_token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default apiClient;
