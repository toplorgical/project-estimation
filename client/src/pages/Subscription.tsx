
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useSubscription, SubscriptionTier } from "@/contexts/SubscriptionContext";
import { authService } from "@/services/authService";
import { useToast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check, CreditCard, WalletCards, Receipt } from "lucide-react";

interface PlanProps {
  name: string;
  price: string;
  description: string;
  features: string[];
  tier: SubscriptionTier;
  popular?: boolean;
}

const SubscriptionPlan: React.FC<PlanProps & {
  isActive: boolean;
  onSubscribe: (tier: SubscriptionTier) => void;
}> = ({ name, price, description, features, tier, popular, isActive, onSubscribe }) => {
  return (
    <Card className={`flex flex-col ${popular ? 'border-estimator-blue ring-1 ring-estimator-blue' : ''} ${isActive ? 'bg-green-50' : ''}`}>
      <CardHeader className={`${popular ? 'bg-estimator-blue text-white' : ''} ${isActive && !popular ? 'bg-green-100' : ''}`}>
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl">{name}</CardTitle>
          {popular && !isActive && <Badge className="bg-white text-estimator-blue">Popular</Badge>}
          {isActive && <Badge className="bg-green-600">Your Plan</Badge>}
        </div>
        <CardDescription className={`${popular ? 'text-white/90' : ''} ${isActive && !popular ? 'text-green-800' : ''}`}>
          {description}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex-grow pt-6">
        <div className="mb-4">
          <p className="text-3xl font-bold">{price}</p>
          <p className="text-sm text-gray-500">per month</p>
        </div>
        <ul className="space-y-2">
          {features.map((feature, index) => (
            <li key={index} className="flex items-start">
              <Check className="h-5 w-5 mr-2 text-green-500 flex-shrink-0" />
              <span className="text-sm">{feature}</span>
            </li>
          ))}
        </ul>
      </CardContent>
      <CardFooter className="pt-4">
        <Button 
          className={`w-full ${isActive 
            ? 'bg-green-600 hover:bg-green-700' 
            : popular 
              ? 'bg-estimator-blue hover:bg-estimator-blue-light' 
              : ''}`}
          disabled={isActive}
          onClick={() => onSubscribe(tier)}
        >
          {isActive ? 'Current Plan' : 'Subscribe'}
        </Button>
      </CardFooter>
    </Card>
  );
};

const Subscription: React.FC = () => {
  const { user } = useAuth();
  const { subscriptionStatus, checkSubscription } = useSubscription();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isProcessing, setIsProcessing] = useState(false);
  
  const plans: PlanProps[] = [
    {
      name: "Free",
      price: "$0",
      description: "Limited access for personal use",
      tier: "free",
      features: [
        "1 estimate per month",
        "Basic project types",
        "Standard calculations",
        "Email support"
      ]
    },
    {
      name: "Basic",
      price: "$9.99",
      description: "Essential features for small projects",
      tier: "basic",
      features: [
        "10 estimates per month",
        "All project types",
        "Advanced calculations",
        "Email and chat support",
        "Export to PDF"
      ]
    },
    {
      name: "Premium",
      price: "$19.99",
      description: "Complete feature set for professionals",
      tier: "premium",
      popular: true,
      features: [
        "Unlimited estimates",
        "All project types",
        "Advanced calculations",
        "Priority support",
        "Export to multiple formats",
        "Team collaboration"
      ]
    },
    {
      name: "Enterprise",
      price: "$49.99",
      description: "Full-featured solution for businesses",
      tier: "enterprise",
      features: [
        "Unlimited estimates",
        "Custom project types",
        "Advanced calculations & reporting",
        "Dedicated support",
        "API access",
        "White-labeling",
        "Team collaboration"
      ]
    }
  ];
  
  const handleSubscribe = async (tier: SubscriptionTier) => {
    if (!user) {
      toast({
        title: "Authentication required",
        description: "Please log in to subscribe to a plan",
        variant: "destructive"
      });
      navigate("/auth");
      return;
    }
    
    setIsProcessing(true);
    
    try {
      // In a real app, this would redirect to Stripe or another payment processor
      // For now, we'll simulate the subscription process
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Set subscription in local storage
      const subscriptionDuration = tier === "free" ? 30 : tier === "basic" ? 30 : tier === "premium" ? 30 : 90;
      authService.activateSubscription(user.id, tier, subscriptionDuration);
      
      // Update subscription context
      await checkSubscription();
      
      toast({
        title: "Subscription activated",
        description: `You are now subscribed to the ${tier.charAt(0).toUpperCase() + tier.slice(1)} plan`,
      });
      
      // Redirect to dashboard
      navigate("/dashboard");
    } catch (error) {
      console.error("Subscription error:", error);
      toast({
        title: "Subscription failed",
        description: "There was an error processing your subscription. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsProcessing(false);
    }
  };
  
  const handleCancelSubscription = async () => {
    if (!user) return;
    
    setIsProcessing(true);
    
    try {
      // In a real app, this would call an API to cancel the subscription
      // For now, we'll simulate the cancellation process
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Cancel subscription in local storage
      authService.cancelSubscription(user.id);
      
      // Update subscription context
      await checkSubscription();
      
      toast({
        title: "Subscription cancelled",
        description: "Your subscription has been cancelled",
      });
    } catch (error) {
      console.error("Cancellation error:", error);
      toast({
        title: "Cancellation failed",
        description: "There was an error cancelling your subscription. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-estimator-blue mb-2">Subscription Plans</h1>
        <p className="text-gray-600">Choose the plan that fits your project estimation needs</p>
      </div>
      
      {subscriptionStatus.isActive && subscriptionStatus.expiresAt && (
        <Card className="mb-8 bg-green-50 border-green-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Receipt className="h-5 w-5" />
              Current Subscription
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col md:flex-row md:items-center justify-between">
              <div>
                <p className="font-medium">
                  You are currently on the {subscriptionStatus.tier.charAt(0).toUpperCase() + subscriptionStatus.tier.slice(1)} plan
                </p>
                <p className="text-sm text-gray-600">
                  Valid until: {subscriptionStatus.expiresAt.toLocaleDateString('en-US', { 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </p>
              </div>
              <Button 
                variant="outline" 
                className="mt-4 md:mt-0 border-red-300 text-red-600 hover:bg-red-50"
                onClick={handleCancelSubscription}
                disabled={isProcessing || subscriptionStatus.tier === "free"}
              >
                {isProcessing ? "Processing..." : "Cancel Subscription"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {plans.map((plan) => (
          <SubscriptionPlan
            key={plan.tier}
            {...plan}
            isActive={subscriptionStatus.tier === plan.tier && subscriptionStatus.isActive}
            onSubscribe={handleSubscribe}
          />
        ))}
      </div>
      
      <div className="mt-12 text-center">
        <div className="inline-flex items-center justify-center p-4 bg-gray-50 rounded-lg border border-gray-200">
          <WalletCards className="h-5 w-5 mr-2 text-gray-500" />
          <span className="text-gray-600 text-sm">
            Secure payments powered by Stripe. Your payment information is never stored on our servers.
          </span>
        </div>
      </div>
    </div>
  );
};

export default Subscription;
