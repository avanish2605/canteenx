import api from './axios';

export const registerStudent = (data) => api.post('/api/auth/register/', data);
export const verifyOtp = (data) => api.post('/api/auth/verify-otp/', data);
export const resendOtp = (data) => api.post('/api/auth/resend-otp/', data);
export const loginUser = (data) => api.post('/api/auth/login/', data);
export const refreshToken = (refresh) => api.post('/api/auth/token/refresh/', { refresh });
export const logoutUser = (refresh) => api.post('/api/auth/logout/', { refresh });
export const updateProfile = (data) => api.patch('/api/auth/profile/', data);
export const changePassword = (data) => api.post('/api/auth/change-password/', data);
export const getProfile = () => api.get('/api/auth/profile/');
export const forgotPassword = (data) => api.post('/api/auth/forgot-password/', data);
export const resetPasswordConfirm = (data) => api.post('/api/auth/reset-password-confirm/', data);

