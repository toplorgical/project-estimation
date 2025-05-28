
import React from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { CostEstimate, ProjectParams } from "@/types";
import { formatCurrency, formatDate } from "@/lib/utils";
import CostBreakdownPieChart from "./CostBreakdownPieChart";
import CostBreakdownTable from "./CostBreakdownTable";
import EstimateEconomicImpact from "./EstimateEconomicImpact";

const EstimateResults: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Get estimate and project data from route state
  const { estimate, projectParams } = location.state as { 
    estimate: CostEstimate; 
    projectParams: ProjectParams;
  } || { estimate: null, projectParams: null };
  
  // Redirect to dashboard if no estimate data is available
  if (!estimate || !projectParams) {
    React.useEffect(() => {
      navigate("/dashboard");
    }, [navigate]);
    
    return <div>Loading...</div>;
  }
  
  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-estimator-blue">{projectParams.title}</h1>
          <p className="text-gray-500">Estimated on {formatDate(estimate.createdAt)}</p>
        </div>
        <div className="flex gap-3">
          <Button 
            variant="outline"
            onClick={() => navigate("/new-estimate")}
          >
            New Estimate
          </Button>
          <Button
            className="bg-estimator-blue hover:bg-estimator-blue-light"
            onClick={() => window.print()}
          >
            Export / Print
          </Button>
        </div>
      </div>
      
      <Card>
        <CardHeader className="bg-estimator-blue rounded-t-lg text-white">
          <CardTitle className="text-2xl">Total Estimated Cost</CardTitle>
          <CardDescription className="text-white text-opacity-90">
            Based on your project specifications
          </CardDescription>
        </CardHeader>
        <CardContent className="py-6">
          <div className="text-center">
            <h2 className="text-4xl font-bold text-estimator-blue mb-2">
              {formatCurrency(estimate.totalCost)}
            </h2>
            <p className="text-gray-500">
              {projectParams.projectSize.value} {projectParams.projectSize.description} • {projectParams.durationInDays} days
            </p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
            <div className="text-center p-3 rounded-lg border bg-gray-50">
              <p className="text-gray-500 text-sm">Labor</p>
              <p className="text-lg font-semibold">{formatCurrency(estimate.laborCost)}</p>
            </div>
            <div className="text-center p-3 rounded-lg border bg-gray-50">
              <p className="text-gray-500 text-sm">Materials</p>
              <p className="text-lg font-semibold">{formatCurrency(estimate.materialCost)}</p>
            </div>
            <div className="text-center p-3 rounded-lg border bg-gray-50">
              <p className="text-gray-500 text-sm">Equipment</p>
              <p className="text-lg font-semibold">{formatCurrency(estimate.equipmentCost)}</p>
            </div>
            <div className="text-center p-3 rounded-lg border bg-gray-50">
              <p className="text-gray-500 text-sm">Overhead</p>
              <p className="text-lg font-semibold">{formatCurrency(estimate.overheadCost)}</p>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Economic Impact Analysis */}
      <EstimateEconomicImpact estimate={estimate} projectParams={projectParams} />
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-1">
          <CardHeader>
            <CardTitle>Project Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h4 className="text-sm font-medium text-gray-500">Project Type</h4>
              <p>{projectParams.projectType.replace("_", " ")}</p>
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-500">Location</h4>
              <p>
                {projectParams.location.city}, {projectParams.location.state && `${projectParams.location.state}, `}
                {projectParams.location.country}
              </p>
            </div>
            <Separator />
            <div>
              <h4 className="text-sm font-medium text-gray-500">Labor</h4>
              <p>{projectParams.skilledLabor} skilled workers, {projectParams.unskilledLabor} unskilled workers</p>
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-500">Size</h4>
              <p>{projectParams.projectSize.value} {projectParams.projectSize.description}</p>
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-500">Duration</h4>
              <p>{projectParams.durationInDays} days</p>
            </div>
            {projectParams.userResources.length > 0 && (
              <>
                <Separator />
                <div>
                  <h4 className="text-sm font-medium text-gray-500">User Resources</h4>
                  <ul className="mt-1 space-y-1">
                    {projectParams.userResources.map((resource, index) => (
                      <li key={index} className="text-sm">
                        {resource.name} ({resource.quantity}) - ${resource.unitCost} per unit
                      </li>
                    ))}
                  </ul>
                </div>
              </>
            )}
          </CardContent>
        </Card>
        
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Cost Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="chart">
              <TabsList className="grid grid-cols-2 mb-4">
                <TabsTrigger value="chart">Chart</TabsTrigger>
                <TabsTrigger value="details">Details</TabsTrigger>
              </TabsList>
              <TabsContent value="chart" className="space-y-4">
                <CostBreakdownPieChart estimate={estimate} />
              </TabsContent>
              <TabsContent value="details" className="space-y-4">
                <CostBreakdownTable estimate={estimate} />
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default EstimateResults;
