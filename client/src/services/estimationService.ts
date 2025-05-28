
import { CostBreakdown, CostEstimate, ProjectParams } from "../types";
import { 
  equipmentCosts,
  laborRates,
  materialCosts,
  overheadFactors,
  regulatoryCosts,
  transportationFactors, 
  utilityCosts
} from "./mockData";
import { generateRandomId } from "../lib/utils";

export const estimationService = {
  // Calculate a cost estimate based on project parameters
  calculateEstimate: (params: ProjectParams): CostEstimate => {
    // Get base labor rates for the country
    const country = params.location.country;
    const baseLabor = laborRates[country] || laborRates["USA"]; // Default to USA rates if country not found
    
    // Apply region factor to base labor rates
    const regionFactor = params.location.regionFactor;
    const adjustedLaborRates = {
      skilled: baseLabor.skilled * regionFactor,
      unskilled: baseLabor.unskilled * regionFactor
    };
    
    // Calculate labor costs (daily rate × number of workers × project duration)
    const skilledLaborCost = adjustedLaborRates.skilled * params.skilledLabor * params.durationInDays * 8; // 8 hours per day
    const unskilledLaborCost = adjustedLaborRates.unskilled * params.unskilledLabor * params.durationInDays * 8; // 8 hours per day
    const totalLaborCost = skilledLaborCost + unskilledLaborCost;
    
    // Calculate material costs based on project type and size
    // For simplicity, we use a base cost per unit and multiply by project size and region factor
    const baseMaterialCost = materialCosts[params.projectType] * params.projectSize.value * regionFactor;
    
    // Deduct user-provided materials from the cost
    const userMaterialsCost = params.userResources
      .filter(resource => resource.type === "material")
      .reduce((total, material) => total + (material.unitCost * material.quantity), 0);
    
    const materialCost = Math.max(0, baseMaterialCost - userMaterialsCost);
    
    // Calculate equipment costs
    const baseEquipmentCost = equipmentCosts[params.projectType] * params.durationInDays;
    
    // Deduct user-provided equipment from the cost
    const userEquipmentCost = params.userResources
      .filter(resource => resource.type === "equipment")
      .reduce((total, equipment) => total + (equipment.unitCost * equipment.quantity), 0);
    
    const equipmentCost = Math.max(0, baseEquipmentCost - userEquipmentCost);
    
    // Calculate utilities costs (per day × duration)
    const utilities = utilityCosts[params.projectType];
    const utilitiesCost = (utilities.power + utilities.water + utilities.fuel + utilities.communication) * params.durationInDays;
    
    // Calculate transportation costs
    const transportFactors = transportationFactors[params.projectType];
    const transportationCost = 
      totalLaborCost * transportFactors.labor +
      materialCost * transportFactors.materials +
      equipmentCost * transportFactors.equipment;
    
    // Calculate regulatory costs
    const regulatory = regulatoryCosts[params.projectType];
    const regulatoryCost = regulatory.permits + regulatory.inspections + regulatory.compliance;
    
    // Calculate overhead costs
    const overhead = overheadFactors[params.projectType];
    const subtotal = totalLaborCost + materialCost + equipmentCost + utilitiesCost + transportationCost + regulatoryCost;
    const overheadCost = 
      subtotal * overhead.management +
      subtotal * overhead.insurance +
      subtotal * overhead.safety +
      subtotal * overhead.miscellaneous;
    
    // Apply economic adjustment based on location
    // This is a simplified approach - in a real app, we'd use actual economic data
    let economicAdjustment = 1.0;
    if (country === "USA") {
      if (params.location.state === "CA" || params.location.state === "NY") {
        economicAdjustment = 1.15; // Higher costs in California and New York
      } else if (params.location.state === "TX" || params.location.state === "FL") {
        economicAdjustment = 0.95; // Lower costs in Texas and Florida
      }
    }
    
    // Calculate total cost with economic adjustment
    const totalCost = (totalLaborCost + materialCost + equipmentCost + utilitiesCost + 
                     transportationCost + regulatoryCost + overheadCost) * economicAdjustment;
    
    // Create a detailed breakdown
    const breakdown: CostBreakdown = {
      labor: {
        skilled: skilledLaborCost,
        unskilled: unskilledLaborCost,
        total: totalLaborCost
      },
      materials: {
        total: materialCost,
        items: [
          { 
            name: "Base Materials", 
            unitCost: materialCosts[params.projectType], 
            quantity: params.projectSize.value, 
            totalCost: baseMaterialCost 
          },
          // Deducting user-provided materials
          ...params.userResources
            .filter(resource => resource.type === "material")
            .map(material => ({
              name: material.name,
              unitCost: -material.unitCost,
              quantity: material.quantity,
              totalCost: -material.unitCost * material.quantity
            }))
        ]
      },
      utilities: {
        power: utilities.power * params.durationInDays,
        water: utilities.water * params.durationInDays,
        fuel: utilities.fuel * params.durationInDays,
        communication: utilities.communication * params.durationInDays,
        total: utilitiesCost
      },
      equipment: {
        rental: baseEquipmentCost * 0.6,
        maintenance: baseEquipmentCost * 0.2,
        purchase: baseEquipmentCost * 0.2,
        total: equipmentCost,
        items: [
          { 
            name: "Required Equipment", 
            unitCost: equipmentCosts[params.projectType], 
            quantity: params.durationInDays, 
            totalCost: baseEquipmentCost
          },
          // Deducting user-provided equipment
          ...params.userResources
            .filter(resource => resource.type === "equipment")
            .map(equipment => ({
              name: equipment.name,
              unitCost: -equipment.unitCost,
              quantity: equipment.quantity,
              totalCost: -equipment.unitCost * equipment.quantity
            }))
        ]
      },
      transportation: {
        labor: totalLaborCost * transportFactors.labor,
        materials: materialCost * transportFactors.materials,
        equipment: equipmentCost * transportFactors.equipment,
        total: transportationCost
      },
      regulatory: {
        permits: regulatory.permits,
        inspections: regulatory.inspections,
        compliance: regulatory.compliance,
        total: regulatoryCost
      },
      overhead: {
        management: subtotal * overhead.management,
        insurance: subtotal * overhead.insurance,
        safety: subtotal * overhead.safety,
        miscellaneous: subtotal * overhead.miscellaneous,
        total: overheadCost
      }
    };
    
    // Create the estimation result
    const estimate: CostEstimate = {
      id: generateRandomId(),
      projectId: params.id || generateRandomId(),
      totalCost,
      laborCost: totalLaborCost,
      materialCost,
      utilitiesCost,
      equipmentCost,
      transportationCost,
      regulatoryCost,
      overheadCost,
      createdAt: new Date(),
      breakdown
    };
    
    return estimate;
  },
  
  // Save an estimate (in a real app, this would store to a database)
  saveEstimate: (estimate: CostEstimate): Promise<CostEstimate> => {
    return new Promise((resolve) => {
      // In a real app, this would save to a database
      // For now, we just return the estimate with a small delay to simulate API call
      setTimeout(() => {
        resolve(estimate);
      }, 300);
    });
  },
  
  // Get a list of saved estimates for a user (in a real app, this would fetch from a database)
  getSavedEstimates: (userId: string): Promise<CostEstimate[]> => {
    return new Promise((resolve) => {
      // In a real app, this would fetch from a database based on user ID
      // For now, we return mock data from mockData.ts
      import("./mockData").then(({ savedEstimates }) => {
        setTimeout(() => {
          resolve(savedEstimates);
        }, 300);
      });
    });
  }
};
