import api from './axios';

export const getCart = () => api.get('/api/cart/');
export const addToCart = (data) => api.post('/api/cart/add/', data);
export const updateCartItem = (itemId, quantity) => api.patch(`/api/cart/items/${itemId}/`, { quantity });
export const removeCartItem = (itemId) => api.delete(`/api/cart/items/${itemId}/`);
export const clearCart = () => api.delete('/api/cart/');
