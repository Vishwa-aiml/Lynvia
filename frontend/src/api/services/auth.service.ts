import apiClient from '../client';

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: 'CLIENT' | 'DESIGNER' | 'ADMIN';
  is_active: boolean;
  created_at: string;
}

export const authService = {
  register: (data: any) => 
    apiClient.post<User>('/auth/register', data),
    
  getMe: () => 
    apiClient.get<User>('/auth/me'),

  forgotPassword: (email: string) =>
    apiClient.post<{ message: string }>('/auth/forgot-password', { email }),
};
