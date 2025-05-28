
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { ProjectParams, ProjectType, Location, UserResource, ProjectSize } from "@/types";
import { locations, projectTypeOptions, projectSizeUnits } from "@/services/mockData";
import { estimationService } from "@/services/estimationService";
import { generateRandomId } from "@/lib/utils";
import ResourceInput from "./ResourceInput";

const EstimationForm: React.FC = () => {
  const { toast } = useToast();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Form data
  const [title, setTitle] = useState("");
  const [projectType, setProjectType] = useState<ProjectType>("residential_building");
  const [location, setLocation] = useState<Location>(locations[0]);
  const [skilledLabor, setSkilledLabor] = useState(5);
  const [unskilledLabor, setUnskilledLabor] = useState(10);
  const [projectSizeValue, setProjectSizeValue] = useState(1000);
  const [durationInDays, setDurationInDays] = useState(30);
  const [userResources, setUserResources] = useState<UserResource[]>([]);
  
  // Current available size unit based on project type
  const [currentSizeUnit, setCurrentSizeUnit] = useState(projectSizeUnits["residential_building"]);
  
  // Update size unit when project type changes
  useEffect(() => {
    setCurrentSizeUnit(projectSizeUnits[projectType]);
  }, [projectType]);
  
  // Add a new user resource
  const handleAddResource = (resource: UserResource) => {
    setUserResources([...userResources, resource]);
  };
  
  // Remove a user resource
  const handleRemoveResource = (index: number) => {
    const updatedResources = [...userResources];
    updatedResources.splice(index, 1);
    setUserResources(updatedResources);
  };
  
  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Simple validation
    if (!title) {
      toast({
        title: "Missing information",
        description: "Please provide a title for your project",
        variant: "destructive",
      });
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      // Create project parameters
      const projectParams: ProjectParams = {
        id: generateRandomId(),
        title,
        projectType,
        location,
        skilledLabor,
        unskilledLabor,
        projectSize: {
          value: projectSizeValue,
          unit: currentSizeUnit.unit,
          description: currentSizeUnit.description,
        },
        durationInDays,
        userResources,
        createdAt: new Date(),
      };
      
      // Calculate estimate
      const estimate = estimationService.calculateEstimate(projectParams);
      
      // Save the estimate
      await estimationService.saveEstimate(estimate);
      
      // Success notification
      toast({
        title: "Estimate created",
        description: "Your project cost estimate has been successfully generated.",
      });
      
      // Navigate to results page with the estimate data
      navigate(`/estimate-result`, { state: { estimate, projectParams } });
    } catch (error) {
      console.error("Estimation error:", error);
      toast({
        title: "Estimation failed",
        description: "An error occurred while generating your estimate. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-2xl text-estimator-blue">Create New Estimate</CardTitle>
        <CardDescription>
          Fill in the details below to get an accurate cost estimate for your project
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form id="estimation-form" onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Project Info */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Project Information</h3>
            
            <div className="space-y-2">
              <Label htmlFor="title">Project Title</Label>
              <Input
                id="title"
                placeholder="Enter a name for your project"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="projectType">Project Type</Label>
                <Select
                  value={projectType}
                  onValueChange={(value: ProjectType) => setProjectType(value)}
                >
                  <SelectTrigger id="projectType">
                    <SelectValue placeholder="Select project type" />
                  </SelectTrigger>
                  <SelectContent>
                    {projectTypeOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="location">Location</Label>
                <Select
                  value={`${location.city}, ${location.state}, ${location.country}`}
                  onValueChange={(value) => {
                    const [city, state, country] = value.split(", ");
                    const selectedLocation = locations.find(
                      (loc) =>
                        loc.city === city &&
                        loc.state === state &&
                        loc.country === country
                    );
                    if (selectedLocation) {
                      setLocation(selectedLocation);
                    }
                  }}
                >
                  <SelectTrigger id="location">
                    <SelectValue placeholder="Select location" />
                  </SelectTrigger>
                  <SelectContent>
                    {locations.map((loc) => (
                      <SelectItem
                        key={`${loc.city}-${loc.state}-${loc.country}`}
                        value={`${loc.city}, ${loc.state}, ${loc.country}`}
                      >
                        {loc.city}, {loc.state ? `${loc.state}, ` : ""}{loc.country}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
          
          <Separator />
          
          {/* Labor & Project Size */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Labor & Project Dimensions</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="skilledLabor">Skilled Workers</Label>
                <Input
                  id="skilledLabor"
                  type="number"
                  min="0"
                  value={skilledLabor}
                  onChange={(e) => setSkilledLabor(parseInt(e.target.value) || 0)}
                />
                <p className="text-xs text-gray-500">
                  Number of skilled workers (e.g., carpenters, electricians)
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="unskilledLabor">Unskilled Workers</Label>
                <Input
                  id="unskilledLabor"
                  type="number"
                  min="0"
                  value={unskilledLabor}
                  onChange={(e) => setUnskilledLabor(parseInt(e.target.value) || 0)}
                />
                <p className="text-xs text-gray-500">
                  Number of unskilled workers (e.g., general laborers)
                </p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="projectSize">
                  Project Size ({currentSizeUnit.description})
                </Label>
                <Input
                  id="projectSize"
                  type="number"
                  min="1"
                  value={projectSizeValue}
                  onChange={(e) => setProjectSizeValue(parseInt(e.target.value) || 0)}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="duration">Project Duration (Days)</Label>
                <Input
                  id="duration"
                  type="number"
                  min="1"
                  value={durationInDays}
                  onChange={(e) => setDurationInDays(parseInt(e.target.value) || 1)}
                />
              </div>
            </div>
          </div>
          
          <Separator />
          
          {/* User Resources */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Resources You'll Provide</h3>
            <p className="text-sm text-gray-500">
              Add any equipment or materials you already have to exclude them from the cost estimate
            </p>
            
            <ResourceInput onAddResource={handleAddResource} />
            
            {userResources.length > 0 && (
              <div className="mt-4">
                <h4 className="text-sm font-medium mb-2">Added Resources:</h4>
                <div className="space-y-2">
                  {userResources.map((resource, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 border rounded-md bg-gray-50"
                    >
                      <div>
                        <p className="font-medium">{resource.name}</p>
                        <p className="text-sm text-gray-500">
                          {resource.type === "equipment" ? "Equipment" : "Material"} • {resource.quantity} units at ${resource.unitCost} per unit
                        </p>
                      </div>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveResource(index)}
                      >
                        Remove
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </form>
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button
          variant="outline"
          onClick={() => navigate("/dashboard")}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          form="estimation-form"
          className="bg-estimator-blue hover:bg-estimator-blue-light"
          disabled={isSubmitting}
        >
          {isSubmitting ? "Calculating..." : "Generate Estimate"}
        </Button>
      </CardFooter>
    </Card>
  );
};

export default EstimationForm;
