
import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { CostEstimate, ProjectParams } from "@/types";
import { estimationService } from "@/services/estimationService";
import EstimateResults from "@/components/estimation/EstimateResults";
import { Button } from "@/components/ui/button";
import { useSubscription } from "@/contexts/SubscriptionContext";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { CreditCard } from "lucide-react";

const EstimateDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [estimate, setEstimate] = useState<CostEstimate | null>(null);
  const [projectParams, setProjectParams] = useState<ProjectParams | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { subscriptionStatus } = useSubscription();
  
  useEffect(() => {
    const loadEstimate = async () => {
      try {
        // In a real app, this would fetch the specific estimate by ID
        // For now, fetch all estimates and find the one with matching ID
        const estimates = await estimationService.getSavedEstimates("");
        const foundEstimate = estimates.find(e => e.id === id);
        
        if (foundEstimate) {
          setEstimate(foundEstimate);
          
          // Mock project params for this demo
          // In a real app, we would fetch the actual project params associated with the estimate
          setProjectParams({
            id: foundEstimate.projectId,
            title: `Project #${foundEstimate.projectId.slice(-4)}`,
            projectType: "residential_building",
            location: { 
              city: "New York", 
              state: "NY", 
              country: "USA", 
              regionFactor: 1.5 
            },
            skilledLabor: 5,
            unskilledLabor: 10,
            projectSize: { value: 1000, unit: "sq_ft", description: "Square Feet" },
            durationInDays: 30,
            userResources: [],
            createdAt: foundEstimate.createdAt,
          });
        }
      } catch (error) {
        console.error("Failed to load estimate:", error);
      } finally {
        setIsLoading(false);
      }
    };
    
    if (id) {
      loadEstimate();
    }
  }, [id]);
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="text-center">
          <p className="text-gray-500">Loading estimate details...</p>
        </div>
      </div>
    );
  }
  
  if (!estimate || !projectParams) {
    return (
      <div className="flex flex-col justify-center items-center min-h-[60vh]">
        <div className="text-center mb-4">
          <h2 className="text-xl font-semibold mb-2">Estimate Not Found</h2>
          <p className="text-gray-500">The estimate you're looking for doesn't exist or has been deleted.</p>
        </div>
        <Button
          onClick={() => navigate("/estimates")}
          variant="outline"
        >
          Back to Saved Estimates
        </Button>
      </div>
    );
  }
  
  return (
    <div className="space-y-4">
      {!subscriptionStatus.isActive && (
        <Alert className="bg-amber-50 border-amber-200 mb-4">
          <AlertDescription className="flex justify-between items-center">
            <div className="flex items-center">
              <CreditCard className="h-4 w-4 mr-2 text-amber-600" />
              <span className="text-amber-800">
                Your subscription is inactive. Some features may be limited.
              </span>
            </div>
            <Button
              size="sm"
              onClick={() => navigate("/subscription")}
              className="bg-amber-600 hover:bg-amber-700 text-white"
            >
              View Plans
            </Button>
          </AlertDescription>
        </Alert>
      )}

      <div className="location-state" data-state={{ estimate, projectParams }}>
        <EstimateResults />
      </div>
    </div>
  );
};

export default EstimateDetail;
