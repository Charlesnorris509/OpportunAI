import api from './api';
import { HttpMethod } from '../types/api';

interface LoginCredentials {
  username: string;
  password: string;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  passwordConfirm: string;
}

interface AuthTokens {
  access: string;
  refresh: string;
}

interface User {
  id: number;
  username: string;
  email: string;
  firstName?: string;
  lastName?: string;
}

class AuthService {
  private static readonly TOKEN_KEY = 'token';
  private static readonly REFRESH_TOKEN_KEY = 'refreshToken';
  private static readonly USER_KEY = 'user';

  async login(credentials: LoginCredentials): Promise<User> {
    try {
      const response = await api.post('/auth/login/', credentials);
      const { access, refresh } = response.data;
      
      // Save tokens and user info
      this.setTokens({ access, refresh });
      
      // Fetch user profile
      const user = await this.getUserProfile();
      
      // Store user data
      localStorage.setItem(AuthService.USER_KEY, JSON.stringify(user));
      
      return user;
    } catch (error) {
      throw error;
    }
  }

  async register(data: RegisterData): Promise<User> {
    try {
      // Validate password match
      if (data.password !== data.passwordConfirm) {
        throw new Error("Passwords don't match");
      }
      
      const response = await api.post('/auth/register/', {
        username: data.username,
        email: data.email,
        password: data.password,
      });
      
      // After registration, login automatically
      return await this.login({
        username: data.username,
        password: data.password,
      });
    } catch (error) {
      throw error;
    }
  }

  async getUserProfile(): Promise<User> {
    try {
      const response = await api.get('/auth/user/');
      return response.data.data;
    } catch (error) {
      throw error;
    }
  }

  logout(): void {
    localStorage.removeItem(AuthService.TOKEN_KEY);
    localStorage.removeItem(AuthService.REFRESH_TOKEN_KEY);
    localStorage.removeItem(AuthService.USER_KEY);
    
    // Redirect to login page
    window.location.href = '/login';
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem(AuthService.TOKEN_KEY);
  }

  getUser(): User | null {
    const userData = localStorage.getItem(AuthService.USER_KEY);
    if (!userData) return null;
    
    try {
      return JSON.parse(userData);
    } catch (e) {
      return null;
    }
  }

  private setTokens(tokens: AuthTokens): void {
    localStorage.setItem(AuthService.TOKEN_KEY, tokens.access);
    localStorage.setItem(AuthService.REFRESH_TOKEN_KEY, tokens.refresh);
  }

  async refreshToken(): Promise<boolean> {
    const refreshToken = localStorage.getItem(AuthService.REFRESH_TOKEN_KEY);
    if (!refreshToken) return false;
    
    try {
      const response = await api.post('/auth/token/refresh/', {
        refresh: refreshToken
      });
      
      const { access } = response.data;
      localStorage.setItem(AuthService.TOKEN_KEY, access);
      return true;
    } catch (error) {
      this.logout();
      return false;
    }
  }
}

export default new AuthService();
