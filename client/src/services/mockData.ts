
import { CostEstimate, Location, ProjectParams, ProjectType } from "../types";
import { generateRandomId } from "../lib/utils";

// Mock project types data
export const projectTypeOptions: { value: ProjectType; label: string }[] = [
  { value: "residential_building", label: "Residential Building" },
  { value: "commercial_building", label: "Commercial Building" },
  { value: "road_construction", label: "Road Construction" },
  { value: "bridge_construction", label: "Bridge Construction" },
  { value: "irrigation", label: "Irrigation System" },
  { value: "manufacturing_setup", label: "Manufacturing Setup" },
  { value: "landscaping", label: "Landscaping" },
  { value: "renovation", label: "Renovation" },
];

// Mock locations data
export const locations: Location[] = [
  { city: "New York", state: "NY", country: "USA", regionFactor: 1.5 },
  { city: "Los Angeles", state: "CA", country: "USA", regionFactor: 1.3 },
  { city: "Chicago", state: "IL", country: "USA", regionFactor: 1.1 },
  { city: "Dallas", state: "TX", country: "USA", regionFactor: 0.9 },
  { city: "Miami", state: "FL", country: "USA", regionFactor: 1.2 },
  { city: "Seattle", state: "WA", country: "USA", regionFactor: 1.25 },
  { city: "Denver", state: "CO", country: "USA", regionFactor: 1.05 },
  { city: "Atlanta", state: "GA", country: "USA", regionFactor: 0.95 },
  { city: "Toronto", state: "ON", country: "Canada", regionFactor: 1.2 },
  { city: "Vancouver", state: "BC", country: "Canada", regionFactor: 1.3 },
  { city: "London", state: "", country: "UK", regionFactor: 1.7 },
  { city: "Berlin", state: "", country: "Germany", regionFactor: 1.4 },
  { city: "Sydney", state: "NSW", country: "Australia", regionFactor: 1.35 },
  { city: "Mumbai", state: "MH", country: "India", regionFactor: 0.7 },
  { city: "Tokyo", state: "", country: "Japan", regionFactor: 1.6 },
];

// Labor rate data by region
export const laborRates: Record<string, { skilled: number; unskilled: number }> = {
  "USA": { skilled: 45, unskilled: 20 },
  "Canada": { skilled: 40, unskilled: 18 },
  "UK": { skilled: 38, unskilled: 16 },
  "Germany": { skilled: 42, unskilled: 19 },
  "Australia": { skilled: 43, unskilled: 21 },
  "India": { skilled: 15, unskilled: 5 },
  "Japan": { skilled: 50, unskilled: 25 },
};

// Material costs by project type (per unit)
export const materialCosts: Record<ProjectType, number> = {
  "residential_building": 150,
  "commercial_building": 200,
  "road_construction": 100,
  "bridge_construction": 300,
  "irrigation": 80,
  "manufacturing_setup": 250,
  "landscaping": 60,
  "renovation": 120
};

// Equipment costs by project type (per day)
export const equipmentCosts: Record<ProjectType, number> = {
  "residential_building": 250,
  "commercial_building": 350,
  "road_construction": 500,
  "bridge_construction": 600,
  "irrigation": 200,
  "manufacturing_setup": 400,
  "landscaping": 150,
  "renovation": 200
};

// Utility costs by project type (per day)
export const utilityCosts: Record<ProjectType, { power: number; water: number; fuel: number; communication: number }> = {
  "residential_building": { power: 50, water: 20, fuel: 30, communication: 10 },
  "commercial_building": { power: 80, water: 30, fuel: 40, communication: 20 },
  "road_construction": { power: 40, water: 30, fuel: 120, communication: 15 },
  "bridge_construction": { power: 60, water: 25, fuel: 150, communication: 15 },
  "irrigation": { power: 25, water: 50, fuel: 30, communication: 10 },
  "manufacturing_setup": { power: 100, water: 40, fuel: 60, communication: 20 },
  "landscaping": { power: 20, water: 60, fuel: 25, communication: 5 },
  "renovation": { power: 40, water: 15, fuel: 25, communication: 10 }
};

// Regulatory costs by project type
export const regulatoryCosts: Record<ProjectType, { permits: number; inspections: number; compliance: number }> = {
  "residential_building": { permits: 2000, inspections: 1000, compliance: 500 },
  "commercial_building": { permits: 5000, inspections: 2000, compliance: 1500 },
  "road_construction": { permits: 3000, inspections: 1500, compliance: 2000 },
  "bridge_construction": { permits: 7000, inspections: 3500, compliance: 4000 },
  "irrigation": { permits: 1500, inspections: 800, compliance: 600 },
  "manufacturing_setup": { permits: 6000, inspections: 2500, compliance: 3000 },
  "landscaping": { permits: 800, inspections: 500, compliance: 300 },
  "renovation": { permits: 1200, inspections: 700, compliance: 400 }
};

// Transportation cost factors by project type
export const transportationFactors: Record<ProjectType, { labor: number; materials: number; equipment: number }> = {
  "residential_building": { labor: 0.05, materials: 0.1, equipment: 0.08 },
  "commercial_building": { labor: 0.06, materials: 0.12, equipment: 0.1 },
  "road_construction": { labor: 0.08, materials: 0.15, equipment: 0.12 },
  "bridge_construction": { labor: 0.1, materials: 0.18, equipment: 0.15 },
  "irrigation": { labor: 0.07, materials: 0.1, equipment: 0.08 },
  "manufacturing_setup": { labor: 0.05, materials: 0.12, equipment: 0.1 },
  "landscaping": { labor: 0.04, materials: 0.08, equipment: 0.06 },
  "renovation": { labor: 0.03, materials: 0.07, equipment: 0.05 }
};

// Overhead cost factors by project type
export const overheadFactors: Record<ProjectType, { management: number; insurance: number; safety: number; miscellaneous: number }> = {
  "residential_building": { management: 0.07, insurance: 0.03, safety: 0.02, miscellaneous: 0.03 },
  "commercial_building": { management: 0.08, insurance: 0.04, safety: 0.03, miscellaneous: 0.03 },
  "road_construction": { management: 0.06, insurance: 0.04, safety: 0.04, miscellaneous: 0.02 },
  "bridge_construction": { management: 0.08, insurance: 0.05, safety: 0.05, miscellaneous: 0.02 },
  "irrigation": { management: 0.05, insurance: 0.02, safety: 0.02, miscellaneous: 0.02 },
  "manufacturing_setup": { management: 0.08, insurance: 0.04, safety: 0.04, miscellaneous: 0.03 },
  "landscaping": { management: 0.05, insurance: 0.02, safety: 0.02, miscellaneous: 0.01 },
  "renovation": { management: 0.06, insurance: 0.03, safety: 0.02, miscellaneous: 0.02 }
};

// Mock project size units by project type
export const projectSizeUnits: Record<ProjectType, { unit: string; description: string }> = {
  "residential_building": { unit: "sq_ft", description: "Square Feet" },
  "commercial_building": { unit: "sq_ft", description: "Square Feet" },
  "road_construction": { unit: "km", description: "Kilometers" },
  "bridge_construction": { unit: "m", description: "Meters" },
  "irrigation": { unit: "acre", description: "Acres" },
  "manufacturing_setup": { unit: "sq_ft", description: "Square Feet" },
  "landscaping": { unit: "acre", description: "Acres" },
  "renovation": { unit: "sq_ft", description: "Square Feet" }
};

// Mock saved user estimates
export const savedEstimates: CostEstimate[] = [
  {
    id: "est-1",
    projectId: "proj-1",
    totalCost: 325000,
    laborCost: 105000,
    materialCost: 120000,
    utilitiesCost: 15000,
    equipmentCost: 35000,
    transportationCost: 12000,
    regulatoryCost: 18000,
    overheadCost: 20000,
    createdAt: new Date(2023, 10, 15),
    breakdown: {
      labor: {
        skilled: 80000,
        unskilled: 25000,
        total: 105000
      },
      materials: {
        total: 120000,
        items: [
          { name: "Concrete", unitCost: 150, quantity: 200, totalCost: 30000 },
          { name: "Steel", unitCost: 1200, quantity: 50, totalCost: 60000 },
          { name: "Finishing Materials", unitCost: 300, quantity: 100, totalCost: 30000 }
        ]
      },
      utilities: {
        power: 6000,
        water: 3000,
        fuel: 4500,
        communication: 1500,
        total: 15000
      },
      equipment: {
        rental: 20000,
        maintenance: 5000,
        purchase: 10000,
        total: 35000,
        items: [
          { name: "Excavator", unitCost: 500, quantity: 20, totalCost: 10000 },
          { name: "Concrete Mixer", unitCost: 300, quantity: 25, totalCost: 7500 },
          { name: "Other Equipment", unitCost: 250, quantity: 70, totalCost: 17500 }
        ]
      },
      transportation: {
        labor: 3000,
        materials: 6000,
        equipment: 3000,
        total: 12000
      },
      regulatory: {
        permits: 10000,
        inspections: 5000,
        compliance: 3000,
        total: 18000
      },
      overhead: {
        management: 10000,
        insurance: 4000,
        safety: 3000,
        miscellaneous: 3000,
        total: 20000
      }
    }
  },
  {
    id: "est-2",
    projectId: "proj-2",
    totalCost: 92000,
    laborCost: 30000,
    materialCost: 25000,
    utilitiesCost: 6000,
    equipmentCost: 15000,
    transportationCost: 4000,
    regulatoryCost: 7000,
    overheadCost: 5000,
    createdAt: new Date(2023, 11, 5),
    breakdown: {
      labor: {
        skilled: 20000,
        unskilled: 10000,
        total: 30000
      },
      materials: {
        total: 25000,
        items: [
          { name: "Plants & Trees", unitCost: 50, quantity: 200, totalCost: 10000 },
          { name: "Soil & Mulch", unitCost: 30, quantity: 300, totalCost: 9000 },
          { name: "Hardscaping Materials", unitCost: 60, quantity: 100, totalCost: 6000 }
        ]
      },
      utilities: {
        power: 1500,
        water: 3000,
        fuel: 1200,
        communication: 300,
        total: 6000
      },
      equipment: {
        rental: 10000,
        maintenance: 2000,
        purchase: 3000,
        total: 15000,
        items: [
          { name: "Small Excavator", unitCost: 300, quantity: 15, totalCost: 4500 },
          { name: "Lawn Equipment", unitCost: 150, quantity: 30, totalCost: 4500 },
          { name: "Other Tools", unitCost: 100, quantity: 60, totalCost: 6000 }
        ]
      },
      transportation: {
        labor: 1000,
        materials: 2000,
        equipment: 1000,
        total: 4000
      },
      regulatory: {
        permits: 4000,
        inspections: 2000,
        compliance: 1000,
        total: 7000
      },
      overhead: {
        management: 2500,
        insurance: 1000,
        safety: 500,
        miscellaneous: 1000,
        total: 5000
      }
    }
  }
];
