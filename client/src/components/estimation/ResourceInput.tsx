
import React, { useState } from "react";
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
import { UserResource } from "@/types";
import { useToast } from "@/components/ui/use-toast";

interface ResourceInputProps {
  onAddResource: (resource: UserResource) => void;
}

const ResourceInput: React.FC<ResourceInputProps> = ({ onAddResource }) => {
  const { toast } = useToast();
  const [resourceType, setResourceType] = useState<"equipment" | "material">("material");
  const [resourceName, setResourceName] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [unitCost, setUnitCost] = useState(0);
  
  const handleAddResource = () => {
    // Validate inputs
    if (!resourceName) {
      toast({
        title: "Missing information",
        description: "Please provide a name for the resource",
        variant: "destructive",
      });
      return;
    }
    
    if (quantity <= 0) {
      toast({
        title: "Invalid quantity",
        description: "Quantity must be greater than zero",
        variant: "destructive",
      });
      return;
    }
    
    if (unitCost <= 0) {
      toast({
        title: "Invalid cost",
        description: "Unit cost must be greater than zero",
        variant: "destructive",
      });
      return;
    }
    
    // Create resource object
    const newResource: UserResource = {
      type: resourceType,
      name: resourceName,
      quantity,
      unitCost,
    };
    
    // Add the resource
    onAddResource(newResource);
    
    // Reset form
    setResourceName("");
    setQuantity(1);
    setUnitCost(0);
  };
  
  return (
    <div className="space-y-4 p-4 border rounded-md bg-gray-50">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="resourceType">Resource Type</Label>
          <Select
            value={resourceType}
            onValueChange={(value: "equipment" | "material") => setResourceType(value)}
          >
            <SelectTrigger id="resourceType">
              <SelectValue placeholder="Select resource type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="material">Material</SelectItem>
              <SelectItem value="equipment">Equipment</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="resourceName">Name</Label>
          <Input
            id="resourceName"
            placeholder={`Enter ${resourceType} name`}
            value={resourceName}
            onChange={(e) => setResourceName(e.target.value)}
          />
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="quantity">Quantity</Label>
          <Input
            id="quantity"
            type="number"
            min="1"
            value={quantity}
            onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="unitCost">Unit Cost ($)</Label>
          <Input
            id="unitCost"
            type="number"
            min="0"
            step="0.01"
            value={unitCost}
            onChange={(e) => setUnitCost(parseFloat(e.target.value) || 0)}
          />
        </div>
      </div>
      
      <Button
        type="button"
        onClick={handleAddResource}
        variant="secondary"
        className="w-full"
      >
        Add Resource
      </Button>
    </div>
  );
};

export default ResourceInput;
