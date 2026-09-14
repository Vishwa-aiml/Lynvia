import { apiClient } from '../client';

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: 'CLIENT' | 'DESIGNER' | 'ADMIN';
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  role: 'CLIENT' | 'DESIGNER' | 'ADMIN';
}

export const authService = {
  login: (data: any) => 
    apiClient.post<AuthResponse>('/auth/login', data),
    
  register: (data: any) => 
    apiClient.post<User>('/auth/register', data),
    
  getMe: () => 
    apiClient.get<User>('/auth/me'),
    
  googleAuth: (token: string, role?: string) => 
    apiClient.post<AuthResponse>('/auth/google', { token, role }),

  forgotPassword: (email: string) =>
    apiClient.post<{ message: string }>('/auth/forgot-password', { email }),
};
