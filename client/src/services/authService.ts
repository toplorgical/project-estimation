
import { User } from "../types";
import { toast } from "@/components/ui/use-toast";
import { SubscriptionTier } from "@/contexts/SubscriptionContext";

// Mock users data 
const users: User[] = [
  { 
    id: "user1", 
    name: "Demo User", 
    email: "demo@example.com", 
    role: "user" 
  },
  { 
    id: "user2", 
    name: "Admin User", 
    email: "admin@example.com", 
    role: "admin" 
  }
];

// Mock subscription data
export interface SubscriptionData {
  isActive: boolean;
  tier: SubscriptionTier;
  expiresAt: Date | null;
}

// Mock authentication service
export const authService = {
  // Current authenticated user
  currentUser: null as User | null,

  // Register a new user
  register: async (name: string, email: string, password: string): Promise<User> => {
    // Check if user already exists
    if (users.some(user => user.email === email)) {
      throw new Error("User with this email already exists");
    }

    // In a real app, we would hash the password and create a user in the DB
    const newUser: User = {
      id: `user${users.length + 1}`,
      name,
      email,
      role: "user"
    };

    // Add the user to our mock database
    users.push(newUser);
    
    // Set the current user
    authService.currentUser = newUser;
    
    // Store in localStorage to persist the session
    localStorage.setItem('currentUser', JSON.stringify(newUser));
    
    // Create default free subscription for new user
    authService.setSubscription(newUser.id, {
      isActive: false,
      tier: "free",
      expiresAt: null
    });
    
    return newUser;
  },

  // Login a user
  login: async (email: string, password: string): Promise<User> => {
    // Find the user in our mock database
    const user = users.find(user => user.email === email);
    
    // Check if user exists
    if (!user) {
      throw new Error("Invalid email or password");
    }
    
    // In a real app, we would compare the hashed password
    // For the mock service, we'll just accept any password
    
    // Set the current user
    authService.currentUser = user;
    
    // Store in localStorage to persist the session
    localStorage.setItem('currentUser', JSON.stringify(user));
    
    return user;
  },

  // Logout the current user
  logout: (): void => {
    authService.currentUser = null;
    localStorage.removeItem('currentUser');
    toast({
      title: "Logged out",
      description: "You have been successfully logged out.",
    });
  },

  // Check if a user is authenticated
  isAuthenticated: (): boolean => {
    return !!authService.currentUser;
  },

  // Initialize the auth service and check for stored user
  initialize: (): void => {
    const storedUser = localStorage.getItem('currentUser');
    if (storedUser) {
      try {
        authService.currentUser = JSON.parse(storedUser) as User;
      } catch (error) {
        console.error("Failed to parse stored user:", error);
        localStorage.removeItem('currentUser');
      }
    }
  },

  // Update user profile
  updateProfile: async (name: string, email: string): Promise<User> => {
    if (!authService.currentUser) {
      throw new Error("User not authenticated");
    }

    // Find the user in our mock database
    const userIndex = users.findIndex(user => user.id === authService.currentUser!.id);
    
    if (userIndex === -1) {
      throw new Error("User not found");
    }

    // Check if email already exists for another user
    const emailExists = users.some(user => user.email === email && user.id !== authService.currentUser!.id);
    if (emailExists) {
      throw new Error("Email already in use by another account");
    }

    // Update user data
    users[userIndex] = {
      ...users[userIndex],
      name,
      email
    };

    // Update the current user
    authService.currentUser = users[userIndex];
    
    // Update localStorage
    localStorage.setItem('currentUser', JSON.stringify(authService.currentUser));
    
    return authService.currentUser;
  },

  // Change user password
  changePassword: async (currentPassword: string, newPassword: string): Promise<void> => {
    if (!authService.currentUser) {
      throw new Error("User not authenticated");
    }

    // In a real app, we would verify the current password here
    // For this mock service, we'll just simulate a successful password change
    
    // Simulate a delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Return success
    return;
  },
  
  // Subscription related methods
  getSubscription: (userId: string): SubscriptionData | null => {
    const storedSubscription = localStorage.getItem(`subscription_${userId}`);
    if (storedSubscription) {
      try {
        const subscription = JSON.parse(storedSubscription);
        if (subscription.expiresAt) {
          subscription.expiresAt = new Date(subscription.expiresAt);
        }
        return subscription;
      } catch (error) {
        console.error("Failed to parse subscription data:", error);
        return null;
      }
    }
    return null;
  },
  
  setSubscription: (userId: string, subscription: SubscriptionData): void => {
    localStorage.setItem(`subscription_${userId}`, JSON.stringify(subscription));
  },
  
  activateSubscription: (userId: string, tier: SubscriptionTier, durationInDays: number = 30): SubscriptionData => {
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + durationInDays);
    
    const subscription: SubscriptionData = {
      isActive: true,
      tier,
      expiresAt
    };
    
    authService.setSubscription(userId, subscription);
    return subscription;
  },
  
  cancelSubscription: (userId: string): void => {
    const subscription = authService.getSubscription(userId);
    if (subscription) {
      subscription.isActive = false;
      authService.setSubscription(userId, subscription);
    }
  }
};

// Initialize the auth service immediately
authService.initialize();
