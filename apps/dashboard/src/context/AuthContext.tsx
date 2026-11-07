import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { authApi, type User, type UserProfileData } from '../services/api';

interface AuthContextType {
  user: User | null;
  profile: UserProfileData | null;
  token: string | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfileData | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('applypilot_token'));
  const [loading, setLoading] = useState<boolean>(true);

  const refreshUser = async () => {
    const storedToken = localStorage.getItem('applypilot_token');
    if (!storedToken) {
      setUser(null);
      setProfile(null);
      setLoading(false);
      return;
    }

    try {
      const data = await authApi.me();
      setUser(data.user);
      setProfile(data.profile);
    } catch {
      localStorage.removeItem('applypilot_token');
      setUser(null);
      setProfile(null);
      setToken(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const login = async (email: string, password: string) => {
    const data = await authApi.login({ email, password });
    localStorage.setItem('applypilot_token', data.token);
    setToken(data.token);
    setUser(data.user);
    setProfile(data.profile);
  };

  const register = async (email: string, password: string, fullName?: string) => {
    const data = await authApi.register({ email, password, full_name: fullName });
    localStorage.setItem('applypilot_token', data.token);
    setToken(data.token);
    setUser(data.user);
    setProfile(data.profile);
  };

  const logout = async () => {
    try {
      if (token) {
        await authApi.logout();
      }
    } catch {
      // Ignore network errors on logout
    } finally {
      localStorage.removeItem('applypilot_token');
      setToken(null);
      setUser(null);
      setProfile(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        token,
        loading,
        isAuthenticated: !!user && !!token,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
