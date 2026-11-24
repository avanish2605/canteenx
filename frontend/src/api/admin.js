import api from './axios';

// Admin Dashboard & Reports
export const getDashboardStats = () => api.get('/api/admin/dashboard/');
export const getAnalytics = (params) => api.get('/api/admin/analytics/', { params });
export const getReports = (params) => api.get('/api/admin/reports/', { params });

// Admin Orders
export const getAdminOrders = (params) => api.get('/api/orders/admin/orders/', { params });
export const updateOrderStatus = (id, data) => api.patch(`/api/orders/admin/orders/${id}/status/`, data);
export const verifyOrderPin = (data) => api.post('/api/orders/admin/verify-pin/', data);

// Food Items Admin
export const getFoodItemsAdmin = (params) => api.get('/api/food/admin/items/', { params });
export const createFoodItem = (data) => api.post('/api/food/admin/items/create/', data);
export const updateFoodItem = (id, data) => api.put(`/api/food/admin/items/${id}/update/`, data);
export const patchFoodItem = (id, data) => api.patch(`/api/food/admin/items/${id}/update/`, data);
export const deleteFoodItem = (id) => api.delete(`/api/food/admin/items/${id}/delete/`);

// Categories Admin
export const getCategoriesAdmin = () => api.get('/api/food/admin/categories/');
export const createCategory = (data) => api.post('/api/food/admin/categories/create/', data);
export const updateCategory = (id, data) => api.put(`/api/food/admin/categories/${id}/`, data);
export const deleteCategory = (id) => api.delete(`/api/food/admin/categories/${id}/`);

// Super Admin
export const getSuperAdminStats = () => api.get('/api/admin/superadmin/stats/');
export const getSuperAdminUsers = (params) => api.get('/api/auth/users/', { params });
export const toggleUserStatus = (id) => api.patch(`/api/auth/users/${id}/toggle-active/`);
export const createCanteenAdmin = (data) => api.post('/api/auth/create-canteen-admin/', data);
export const getSuperAdminCanteens = () => api.get('/api/canteens/');
export const createCanteen = (data) => api.post('/api/canteens/create/', data);
export const updateCanteen = (id, data) => api.put(`/api/canteens/${id}/update/`, data);
