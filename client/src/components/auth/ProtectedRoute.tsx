
import React, { useEffect } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useSubscription } from "@/contexts/SubscriptionContext";
import { useToast } from "@/components/ui/use-toast";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

// Routes that require an active subscription
const subscriptionRequiredRoutes = [
  "/new-estimate"
];

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const { subscriptionStatus, isLoading: subscriptionLoading } = useSubscription();
  const location = useLocation();
  const { toast } = useToast();
  
  // Show authentication toast only when auth status changes
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      toast({
        title: "Authentication required",
        description: "Please log in to access this page",
        variant: "destructive",
      });
    }
  }, [loading, isAuthenticated, toast]);
  
  // Check if the current path requires a subscription
  const requiresSubscription = subscriptionRequiredRoutes.some(route => 
    location.pathname.startsWith(route)
  );
  
  // Show subscription toast only when relevant conditions change
  useEffect(() => {
    if (isAuthenticated && 
        !subscriptionLoading && 
        requiresSubscription && 
        !subscriptionStatus.isActive) {
      toast({
        title: "Subscription required",
        description: "You need an active subscription to access this feature",
        variant: "destructive",
      });
    }
  }, [isAuthenticated, subscriptionLoading, requiresSubscription, subscriptionStatus.isActive, toast]);
  
  if (loading || subscriptionLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <p className="text-gray-500">Loading...</p>
        </div>
      </div>
    );
  }
  
  // Redirect to subscription page if subscription is required but not active
  if (isAuthenticated && requiresSubscription && !subscriptionStatus.isActive) {
    return <Navigate to="/subscription" state={{ from: location }} replace />;
  }
  
  return isAuthenticated ? (
    <>{children}</>
  ) : (
    <Navigate to="/auth" state={{ from: location }} replace />
  );
};

export default ProtectedRoute;
