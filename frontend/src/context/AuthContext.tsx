import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiClient } from '../services/api';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  role: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: any) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [role, setRole] = useState<string | null>(localStorage.getItem('user_role'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const fetchCurrentUser = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setIsLoading(false);
      return;
    }
    try {
      const res = await apiClient.get('/auth/me');
      setUser(res.data);
      setRole(res.data.role);
      localStorage.setItem('user_role', res.data.role);
    } catch (err) {
      localStorage.clear();
      setUser(null);
      setRole(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCurrentUser();
  }, []);

  const login = async (credentials: any) => {
    const res = await apiClient.post('/auth/login', credentials);
    const { access_token, refresh_token, role, user_id, full_name } = res.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    localStorage.setItem('user_role', role);
    setRole(role);
    setUser({ id: user_id, email: credentials.email, full_name, role, is_active: true });
  };

  const register = async (formData: any) => {
    const res = await apiClient.post('/auth/register', formData);
    const { access_token, refresh_token, role, user_id, full_name } = res.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    localStorage.setItem('user_role', role);
    setRole(role);
    setUser({ id: user_id, email: formData.email, full_name, role, is_active: true });
  };

  const logout = () => {
    localStorage.clear();
    setUser(null);
    setRole(null);
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider value={{ user, role, isAuthenticated: !!user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
