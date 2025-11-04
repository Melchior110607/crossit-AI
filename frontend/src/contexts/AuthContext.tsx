'use client';

import React, { createContext, useContext } from 'react';
import { useSession, signOut as authSignOut } from '@/lib/auth-client';

interface User {
  id: string;
  email: string;
  name?: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  // Utiliser le hook useSession de Better Auth
  const { data: session, isPending } = useSession();

  const logout = async () => {
    try {
      await authSignOut();
      window.location.href = '/signin';
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <AuthContext.Provider value={{ 
      user: session?.user || null, 
      loading: isPending,
      logout 
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

