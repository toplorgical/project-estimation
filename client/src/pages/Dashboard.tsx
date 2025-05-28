
import React, { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { CostEstimate } from "@/types";
import { estimationService } from "@/services/estimationService";
import DashboardSummary from "@/components/dashboard/DashboardSummary";

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [estimates, setEstimates] = useState<CostEstimate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Load estimates on component mount
  useEffect(() => {
    const loadEstimates = async () => {
      if (!user) return;
      
      try {
        const fetchedEstimates = await estimationService.getSavedEstimates(user.id);
        setEstimates(fetchedEstimates);
      } catch (error) {
        console.error("Failed to load estimates:", error);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadEstimates();
  }, [user]);
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="text-center">
          <p className="text-gray-500">Loading dashboard...</p>
        </div>
      </div>
    );
  }
  
  return <DashboardSummary recentEstimates={estimates} totalEstimates={estimates.length} />;
};

export default Dashboard;
