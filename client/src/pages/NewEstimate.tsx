
import React from "react";
import { useNavigate } from "react-router-dom";
import EstimationForm from "@/components/estimation/EstimationForm";
import { useSubscription } from "@/contexts/SubscriptionContext";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { CreditCard } from "lucide-react";

const NewEstimate: React.FC = () => {
  const { subscriptionStatus, isLoading } = useSubscription();
  const navigate = useNavigate();
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh]">
        <div className="text-center">
          <p className="text-gray-500">Checking subscription status...</p>
        </div>
      </div>
    );
  }
  
  // If user doesn't have an active subscription, show subscription required message
  if (!subscriptionStatus.isActive) {
    return (
      <div className="max-w-3xl mx-auto">
        <Card className="border-amber-200 bg-amber-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-amber-700">
              <CreditCard className="h-5 w-5" />
              Subscription Required
            </CardTitle>
            <CardDescription className="text-amber-600">
              You need an active subscription to create new estimates
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="py-4 text-center">
              <p className="mb-6 text-gray-700">
                To create and manage project estimates, please subscribe to one of our plans.
                Our subscription plans provide access to all estimation features and regular updates.
              </p>
              <div className="flex justify-center">
                <Button 
                  onClick={() => navigate("/subscription")}
                  className="bg-estimator-blue hover:bg-estimator-blue-light"
                >
                  View Subscription Plans
                </Button>
              </div>
            </div>
          </CardContent>
          <CardFooter className="bg-amber-100/50 text-sm text-amber-700">
            Already subscribed? Try refreshing the page or contact support if the issue persists.
          </CardFooter>
        </Card>
      </div>
    );
  }
  
  // If subscription is active, show estimation form
  return (
    <div className="max-w-3xl mx-auto">
      <EstimationForm />
    </div>
  );
};

export default NewEstimate;
