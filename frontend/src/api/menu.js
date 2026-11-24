import api from './axios';

export const getCanteens = () => api.get('/api/canteens/');
export const getCategories = (params) => api.get('/api/food/categories/', { params });
export const getFoodItems = (params) => api.get('/api/food/items/', { params });
export const getFoodItem = (id) => api.get(`/api/food/items/${id}/`);
export const getFeaturedItems = () => api.get('/api/food/items/', { params: { is_featured: true } });
export const getPopularItems = () => api.get('/api/food/items/', { params: { ordering: '-total_orders', page_size: 8 } });
