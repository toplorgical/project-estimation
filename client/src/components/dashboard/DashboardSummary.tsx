import React from "react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { CostEstimate } from "@/types";
import { formatCurrency, formatDate } from "@/lib/utils";
import { useSubscription } from "@/contexts/SubscriptionContext";
import { CreditCard, Receipt } from "lucide-react";

interface DashboardSummaryProps {
  recentEstimates: CostEstimate[];
  totalEstimates: number;
}

const DashboardSummary: React.FC<DashboardSummaryProps> = ({ recentEstimates, totalEstimates }) => {
  const navigate = useNavigate();
  const { subscriptionStatus } = useSubscription();
  
  // Calculate total project value
  const totalValue = recentEstimates.reduce((sum, estimate) => sum + estimate.totalCost, 0);
  
  // Get highest cost project
  const highestCostProject = recentEstimates.length > 0
    ? recentEstimates.reduce((prev, current) => 
        prev.totalCost > current.totalCost ? prev : current
      )
    : null;

  return (
    <div className="space-y-6">
      {/* Subscription Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className={`col-span-1 lg:col-span-3 ${
          subscriptionStatus.isActive 
            ? "bg-green-50 border-green-200" 
            : "bg-amber-50 border-amber-200"
        }`}>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg flex items-center gap-2">
              <CreditCard className="h-5 w-5" />
              Subscription Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between">
              <div>
                {subscriptionStatus.isActive ? (
                  <div>
                    <p className="font-medium text-green-700">
                      {subscriptionStatus.tier.charAt(0).toUpperCase() + subscriptionStatus.tier.slice(1)} Plan Active
                    </p>
                    {subscriptionStatus.expiresAt && (
                      <p className="text-sm text-green-600">
                        Valid until {subscriptionStatus.expiresAt.toLocaleDateString('en-US', { 
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric' 
                        })}
                      </p>
                    )}
                  </div>
                ) : (
                  <p className="font-medium text-amber-700">
                    No active subscription
                  </p>
                )}
              </div>
              <Button 
                onClick={() => navigate("/subscription")}
                className={`mt-3 sm:mt-0 ${
                  subscriptionStatus.isActive 
                    ? "bg-green-600 hover:bg-green-700" 
                    : "bg-estimator-blue hover:bg-estimator-blue-light"
                }`}
                size="sm"
              >
                {subscriptionStatus.isActive ? "Manage Subscription" : "View Plans"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Other dashboard content */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Total Projects</CardTitle>
            <CardDescription>Number of projects estimated</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold text-estimator-blue">{totalEstimates}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Total Project Value</CardTitle>
            <CardDescription>Combined value of recent projects</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold text-estimator-blue">{formatCurrency(totalValue)}</div>
          </CardContent>
        </Card>
        
        {highestCostProject && (
          <Card>
            <CardHeader>
              <CardTitle>Highest Cost Project</CardTitle>
              <CardDescription>Most expensive project recently estimated</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-xl font-semibold text-estimator-blue">{highestCostProject.projectId.slice(-4)}</div>
              <p className="text-sm text-gray-500">
                {formatCurrency(highestCostProject.totalCost)} on {formatDate(highestCostProject.createdAt)}
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Recent Estimates */}
      {recentEstimates.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Recent Estimates</CardTitle>
            <CardDescription>Your most recent project cost estimates</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recentEstimates.map((estimate) => (
                <div key={estimate.id} className="border rounded-md p-4 bg-gray-50">
                  <div className="font-medium text-estimator-blue">Project #{estimate.projectId.slice(-4)}</div>
                  <div className="text-sm text-gray-500">
                    {formatCurrency(estimate.totalCost)} on {formatDate(estimate.createdAt)}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
          <CardFooter>
            <Button
              onClick={() => navigate("/estimates")}
              variant="outline"
            >
              View All Estimates
            </Button>
          </CardFooter>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Recent Estimates</CardTitle>
            <CardDescription>You haven't created any estimates yet</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center py-8">
            <p className="text-gray-500 mb-4 text-center">
              Start by creating your first project cost estimate
            </p>
            <Button
              onClick={() => navigate("/new-estimate")}
              className="bg-estimator-blue hover:bg-estimator-blue-light"
              disabled={!subscriptionStatus.isActive}
            >
              {subscriptionStatus.isActive ? "Create New Estimate" : "Subscribe to Create Estimate"}
            </Button>
            {!subscriptionStatus.isActive && (
              <p className="text-xs text-amber-600 mt-2">
                Active subscription required to create estimates
              </p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default DashboardSummary;
