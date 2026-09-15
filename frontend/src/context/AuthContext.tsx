import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../api/services/auth.service';
import type { User } from '../api/services/auth.service';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import type { User as FirebaseUser } from 'firebase/auth';
import { auth } from '../config/firebase';

interface AuthContextType {
  user: User | null;
  role: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [role, setRole] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // Listen to Firebase auth state changes
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser: FirebaseUser | null) => {
      if (firebaseUser) {
        // Wait for token to be available, then fetch our custom backend user profile
        await fetchUser();
      } else {
        // User logged out from Firebase
        setUser(null);
        setRole(null);
        setIsLoading(false);
      }
    });

    return () => unsubscribe();
  }, []);

  const fetchUser = async () => {
    try {
      setIsLoading(true);
      // Wait briefly if Firebase just fired the onAuthStateChanged to ensure ID token is ready
      // apiClient handles injecting the token.
      const response = await authService.getMe();
      setUser(response.data);
      setRole(response.data.role);
    } catch (error) {
      console.error('Failed to fetch backend user profile:', error);
      // If we can't get the backend profile (maybe deleted), we should sign out of Firebase too.
      await logout();
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await signOut(auth);
    } catch (error) {
      console.error('Firebase sign out error:', error);
    }
    setUser(null);
    setRole(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        isAuthenticated: !!user,
        isLoading,
        logout,
        fetchUser,
      }}
    >
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
