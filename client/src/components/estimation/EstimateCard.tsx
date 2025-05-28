
import React from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CostEstimate } from "@/types";
import { formatCurrency, formatDate } from "@/lib/utils";

interface EstimateCardProps {
  estimate: CostEstimate;
}

const EstimateCard: React.FC<EstimateCardProps> = ({ estimate }) => {
  const navigate = useNavigate();
  
  return (
    <Card className="transition-shadow hover:shadow-md">
      <CardContent className="p-6">
        <div className="mb-4">
          <p className="text-sm text-gray-500">{formatDate(estimate.createdAt)}</p>
          <h3 className="text-xl font-bold mt-1 text-estimator-blue">
            Project #{estimate.projectId.slice(-4)}
          </h3>
        </div>
        
        <div className="flex justify-between items-baseline mb-4">
          <span className="text-gray-500">Total Cost</span>
          <span className="text-2xl font-bold">{formatCurrency(estimate.totalCost)}</span>
        </div>
        
        <div className="grid grid-cols-2 gap-3">
          <div className="border rounded p-2 bg-gray-50 text-center">
            <span className="text-xs text-gray-500">Labor</span>
            <p className="font-medium">{formatCurrency(estimate.laborCost)}</p>
          </div>
          <div className="border rounded p-2 bg-gray-50 text-center">
            <span className="text-xs text-gray-500">Materials</span>
            <p className="font-medium">{formatCurrency(estimate.materialCost)}</p>
          </div>
        </div>
      </CardContent>
      <CardFooter className="px-6 py-4 bg-gray-50 border-t">
        <Button 
          onClick={() => navigate(`/estimate/${estimate.id}`)} 
          variant="outline" 
          className="w-full"
        >
          View Details
        </Button>
      </CardFooter>
    </Card>
  );
};

export default EstimateCard;
