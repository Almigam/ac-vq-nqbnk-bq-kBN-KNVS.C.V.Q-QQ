import { createContext, useState, useCallback, ReactNode, useEffect } from 'react';
import { User } from '../api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (user: User, token: string, refreshToken?: string) => void;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem('user');
    return stored ? JSON.parse(stored) : null;
  });

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Verificar autenticación al iniciar
    const verifyAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        // Verificar que el token sea válido
        const response = await fetch(
          `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/v1/auth/verify`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.ok) {
          // Token válido
          const stored = localStorage.getItem('user');
          if (stored) {
            setUser(JSON.parse(stored));
          }
        } else if (response.status === 401) {
          // Token expirado, intentar refresh
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              const refreshResponse = await fetch(
                `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/v1/auth/refresh`,
                {
                  method: 'POST',
                  headers: {
                    Authorization: `Bearer ${refreshToken}`,
                  },
                }
              );

              if (refreshResponse.ok) {
                const data = await refreshResponse.json();
                localStorage.setItem('access_token', data.access_token);
                const stored = localStorage.getItem('user');
                if (stored) {
                  setUser(JSON.parse(stored));
                }
              } else {
                logout();
              }
            } catch {
              logout();
            }
          } else {
            logout();
          }
        }
      } catch (error) {
        console.error('Auth verification error:', error);
      } finally {
        setIsLoading(false);
      }
    };

    verifyAuth();
  }, []);

  const login = useCallback((userData: User, token: string, refreshToken?: string) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('access_token', token);
    if (refreshToken) {
      localStorage.setItem('refresh_token', refreshToken);
    }
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }, []);

  const refreshToken = useCallback(async () => {
    const token = localStorage.getItem('refresh_token');
    if (!token) {
      logout();
      throw new Error('No refresh token available');
    }

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/v1/auth/refresh`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        logout();
        throw new Error('Refresh failed');
      }

      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
    } catch (error) {
      logout();
      throw error;
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, logout, refreshToken }}>
      {children}
    </AuthContext.Provider>
  );
}
