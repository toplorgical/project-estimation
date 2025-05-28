
// Auth types
export type User = {
  id: string;
  name: string;
  email: string;
  role: "user" | "admin";
};

// Project types
export type ProjectType = 
  | "residential_building" 
  | "commercial_building" 
  | "road_construction" 
  | "bridge_construction"
  | "irrigation" 
  | "manufacturing_setup" 
  | "landscaping" 
  | "renovation";

export type ProjectSize = {
  value: number;
  unit: string;
  description: string;
};

export type Location = {
  city: string;
  state: string;
  country: string;
  regionFactor: number; // Cost multiplier for region
};

export interface ProjectParams {
  id?: string;
  title: string;
  projectType: ProjectType;
  location: Location;
  skilledLabor: number;
  unskilledLabor: number;
  projectSize: ProjectSize;
  durationInDays: number;
  userResources: UserResource[];
  createdAt?: Date;
  userId?: string;
}

export interface UserResource {
  type: "equipment" | "material";
  name: string;
  quantity: number;
  unitCost: number;
}

// Cost breakdown types
export interface CostEstimate {
  id: string;
  projectId: string;
  totalCost: number;
  laborCost: number;
  materialCost: number;
  utilitiesCost: number;
  equipmentCost: number;
  transportationCost: number;
  regulatoryCost: number;
  overheadCost: number;
  createdAt: Date;
  breakdown: CostBreakdown;
}

export interface CostBreakdown {
  labor: {
    skilled: number;
    unskilled: number;
    total: number;
  };
  materials: {
    total: number;
    items: CostItem[];
  };
  utilities: {
    power: number;
    water: number;
    fuel: number;
    communication: number;
    total: number;
  };
  equipment: {
    rental: number;
    maintenance: number;
    purchase: number;
    total: number;
    items: CostItem[];
  };
  transportation: {
    labor: number;
    materials: number;
    equipment: number;
    total: number;
  };
  regulatory: {
    permits: number;
    inspections: number;
    compliance: number;
    total: number;
  };
  overhead: {
    management: number;
    insurance: number;
    safety: number;
    miscellaneous: number;
    total: number;
  };
}

export interface CostItem {
  name: string;
  unitCost: number;
  quantity: number;
  totalCost: number;
}
