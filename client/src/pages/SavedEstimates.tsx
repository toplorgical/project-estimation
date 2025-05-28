
import React, { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { CostEstimate } from "@/types";
import { estimationService } from "@/services/estimationService";
import EstimateCard from "@/components/estimation/EstimateCard";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";

const SavedEstimates: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
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
          <p className="text-gray-500">Loading estimates...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-estimator-blue">Saved Estimates</h1>
          <p className="text-gray-500">Review and manage your saved project estimates</p>
        </div>
        <Button 
          className="bg-estimator-blue hover:bg-estimator-blue-light"
          onClick={() => navigate("/new-estimate")}
        >
          New Estimate
        </Button>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Your Estimates</CardTitle>
          <CardDescription>
            All your project cost estimates in one place
          </CardDescription>
        </CardHeader>
        <CardContent>
          {estimates.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {estimates.map((estimate) => (
                <EstimateCard key={estimate.id} estimate={estimate} />
              ))}
            </div>
          ) : (
            <div className="text-center py-10">
              <p className="text-gray-500 mb-4">
                You don't have any saved estimates yet.
              </p>
              <Button
                onClick={() => navigate("/new-estimate")}
                className="bg-estimator-blue hover:bg-estimator-blue-light"
              >
                Create Your First Estimate
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default SavedEstimates;
