
import React, { createContext, useContext, useEffect, useState } from "react";
import { User } from "../types";
import { authService } from "../services/authService";
import { useToast } from "@/components/ui/use-toast";

// Define the context shape
interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

// Create the context with a default value
const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: async () => {},
  register: async () => {},
  logout: () => {},
  isAuthenticated: false,
});

// Hook to use the auth context
export const useAuth = () => useContext(AuthContext);

// Provider component that wraps the app and makes auth object available
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  // Check for stored user on initial load
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Initialize our auth service
        authService.initialize();
        
        // Set the user from the auth service
        setUser(authService.currentUser);
      } catch (error) {
        console.error("Auth initialization error:", error);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // Register a new user
  const register = async (name: string, email: string, password: string) => {
    try {
      setLoading(true);
      const newUser = await authService.register(name, email, password);
      setUser(newUser);
      toast({
        title: "Registration successful",
        description: "Welcome to the Project Cost Estimator!",
      });
    } catch (error) {
      console.error("Registration error:", error);
      toast({
        title: "Registration failed",
        description: error instanceof Error ? error.message : "An error occurred during registration",
        variant: "destructive",
      });
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Login a user
  const login = async (email: string, password: string) => {
    try {
      setLoading(true);
      const loggedInUser = await authService.login(email, password);
      setUser(loggedInUser);
      toast({
        title: "Login successful",
        description: `Welcome back, ${loggedInUser.name}!`,
      });
    } catch (error) {
      console.error("Login error:", error);
      toast({
        title: "Login failed",
        description: error instanceof Error ? error.message : "Invalid email or password",
        variant: "destructive",
      });
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Logout the current user
  const logout = () => {
    authService.logout();
    setUser(null);
  };

  // Value to provide through the context
  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
