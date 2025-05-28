
import React, { createContext, useContext, useState, useEffect } from "react";
import { useAuth } from "./AuthContext";
import { useToast } from "@/components/ui/use-toast";

// Define subscription tiers
export type SubscriptionTier = "free" | "basic" | "premium" | "enterprise";

export interface SubscriptionStatus {
  isActive: boolean;
  tier: SubscriptionTier;
  expiresAt: Date | null;
}

interface SubscriptionContextType {
  subscriptionStatus: SubscriptionStatus;
  checkSubscription: () => Promise<void>;
  isLoading: boolean;
}

const defaultSubscriptionStatus: SubscriptionStatus = {
  isActive: false,
  tier: "free",
  expiresAt: null
};

const SubscriptionContext = createContext<SubscriptionContextType>({
  subscriptionStatus: defaultSubscriptionStatus,
  checkSubscription: async () => {},
  isLoading: false
});

export const useSubscription = () => useContext(SubscriptionContext);

export const SubscriptionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const { toast } = useToast();
  const [subscriptionStatus, setSubscriptionStatus] = useState<SubscriptionStatus>(defaultSubscriptionStatus);
  const [isLoading, setIsLoading] = useState(false);

  // Function to check and update subscription status
  const checkSubscription = async () => {
    if (!isAuthenticated || !user) {
      setSubscriptionStatus(defaultSubscriptionStatus);
      return;
    }

    setIsLoading(true);
    try {
      // In a real implementation, this would make an API call to check subscription status
      // For now, we'll simulate this with mock data from localStorage
      const storedSubscription = localStorage.getItem(`subscription_${user.id}`);
      
      if (storedSubscription) {
        const parsedStatus = JSON.parse(storedSubscription);
        
        // Check if subscription has expired
        const expiresAt = parsedStatus.expiresAt ? new Date(parsedStatus.expiresAt) : null;
        const isActive = expiresAt ? new Date() < expiresAt : parsedStatus.isActive;
        
        setSubscriptionStatus({
          isActive,
          tier: parsedStatus.tier,
          expiresAt: expiresAt
        });
      } else {
        // Default to free tier for new users
        setSubscriptionStatus({
          isActive: false,
          tier: "free",
          expiresAt: null
        });
      }
    } catch (error) {
      console.error("Failed to check subscription status:", error);
      toast({
        title: "Subscription Check Failed",
        description: "Unable to verify your subscription status. Please try again later.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Check subscription when user changes
  useEffect(() => {
    checkSubscription();
  }, [user, isAuthenticated]);

  return (
    <SubscriptionContext.Provider value={{
      subscriptionStatus,
      checkSubscription,
      isLoading
    }}>
      {children}
    </SubscriptionContext.Provider>
  );
};
