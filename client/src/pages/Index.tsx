
import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

const Index: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <p className="text-gray-500">Loading...</p>
        </div>
      </div>
    );
  }
  
  // Redirect to dashboard if authenticated, otherwise to login page
  return isAuthenticated ? <Navigate to="/dashboard" /> : <Navigate to="/auth" />;
};

export default Index;
