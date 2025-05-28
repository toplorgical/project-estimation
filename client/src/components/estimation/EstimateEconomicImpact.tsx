
import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ProjectParams, CostEstimate } from "@/types";
import { TrendingUp, TrendingDown, DollarSign } from "lucide-react";
import { formatCurrency } from "@/lib/utils";

interface EstimateEconomicImpactProps {
  estimate: CostEstimate;
  projectParams: ProjectParams;
}

const EstimateEconomicImpact: React.FC<EstimateEconomicImpactProps> = ({ 
  estimate, 
  projectParams 
}) => {
  // Economic impact factors based on location
  const getLocationImpact = () => {
    const { location } = projectParams;
    const country = location.country;
    const city = location.city;
    
    // Economic data (in a real app, this would come from an API)
    const economicData = {
      USA: {
        inflationRate: 3.7,
        growthRate: 2.1,
        constructionGrowth: 4.3,
        laborMarketTightness: "high",
        materialShortages: ["lumber", "steel"]
      },
      Canada: {
        inflationRate: 3.1,
        growthRate: 1.8,
        constructionGrowth: 3.5,
        laborMarketTightness: "medium",
        materialShortages: ["concrete"]
      },
      UK: {
        inflationRate: 4.2,
        growthRate: 1.4,
        constructionGrowth: 2.9,
        laborMarketTightness: "medium",
        materialShortages: ["bricks", "timber"]
      }
    };
    
    // Default to USA if country not found
    const countryData = economicData[country as keyof typeof economicData] || economicData.USA;
    
    // Calculate impact factors (these would be more sophisticated in a real app)
    const inflationImpact = countryData.inflationRate / 100 * estimate.totalCost;
    const growthOpportunity = countryData.constructionGrowth / 100 * estimate.totalCost;
    const laborMarketImpact = countryData.laborMarketTightness === "high" ? 0.05 * estimate.laborCost : 0.02 * estimate.laborCost;
    
    return {
      countryData,
      inflationImpact,
      growthOpportunity,
      laborMarketImpact,
      location: `${city}, ${location.state ? location.state + ', ' : ''}${country}`
    };
  };
  
  const impact = getLocationImpact();
  
  // Calculate potential cost in 1 year with inflation
  const futureCost = estimate.totalCost + impact.inflationImpact;
  
  // Determine if current economic conditions are favorable
  const isFavorableEconomy = impact.countryData.constructionGrowth > impact.countryData.inflationRate;
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <DollarSign className="h-5 w-5" />
          Economic Impact Analysis
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-sm text-gray-500 mb-2">
          Based on economic conditions in {impact.location}
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="border rounded-lg p-4 bg-gray-50">
            <div className="text-sm text-gray-500 mb-1">Current Inflation Rate</div>
            <div className="text-xl font-semibold text-estimator-blue flex items-center">
              {impact.countryData.inflationRate}%
              <TrendingUp className="ml-2 h-4 w-4 text-amber-500" />
            </div>
            <div className="mt-2 text-sm text-gray-600">
              Potential impact: {formatCurrency(impact.inflationImpact)} in additional costs over 1 year
            </div>
          </div>
          
          <div className="border rounded-lg p-4 bg-gray-50">
            <div className="text-sm text-gray-500 mb-1">Construction Industry Growth</div>
            <div className="text-xl font-semibold text-estimator-blue flex items-center">
              {impact.countryData.constructionGrowth}%
              {impact.countryData.constructionGrowth > 0 ? (
                <TrendingUp className="ml-2 h-4 w-4 text-green-500" />
              ) : (
                <TrendingDown className="ml-2 h-4 w-4 text-red-500" />
              )}
            </div>
            <div className="mt-2 text-sm text-gray-600">
              Sector outlook: {impact.countryData.constructionGrowth > 3 ? 'Positive' : 'Moderate'}
            </div>
          </div>
        </div>
        
        <Alert className={isFavorableEconomy ? "bg-green-50 border-green-200" : "bg-amber-50 border-amber-200"}>
          <AlertDescription>
            <div className="flex items-center justify-between">
              <div>
                <span className="font-medium">Economic outlook:</span> {isFavorableEconomy ? 'Favorable' : 'Challenging'} for this project
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-600">Projected cost in 1 year:</div>
                <div className="font-semibold">{formatCurrency(futureCost)}</div>
              </div>
            </div>
          </AlertDescription>
        </Alert>
        
        {impact.countryData.materialShortages.length > 0 && (
          <div className="border-t pt-3 mt-3">
            <div className="text-sm font-medium mb-1">Material Supply Considerations:</div>
            <div className="text-sm text-gray-600">
              Current shortages of {impact.countryData.materialShortages.join(", ")} may affect project timeline and costs.
            </div>
          </div>
        )}
        
        <div className="text-sm text-gray-400 mt-2">
          Note: This analysis is based on regional economic data and represents an estimate only.
        </div>
      </CardContent>
    </Card>
  );
};

export default EstimateEconomicImpact;
