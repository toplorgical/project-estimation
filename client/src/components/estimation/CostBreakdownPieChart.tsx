
import React from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import { CostEstimate } from "@/types";
import { formatCurrency } from "@/lib/utils";

interface CostBreakdownPieChartProps {
  estimate: CostEstimate;
}

const CostBreakdownPieChart: React.FC<CostBreakdownPieChartProps> = ({ estimate }) => {
  // Prepare data for the pie chart
  const data = [
    { name: "Labor", value: estimate.laborCost },
    { name: "Materials", value: estimate.materialCost },
    { name: "Equipment", value: estimate.equipmentCost },
    { name: "Utilities", value: estimate.utilitiesCost },
    { name: "Transportation", value: estimate.transportationCost },
    { name: "Regulatory", value: estimate.regulatoryCost },
    { name: "Overhead", value: estimate.overheadCost },
  ];
  
  // Filter out zero values
  const filteredData = data.filter(item => item.value > 0);
  
  // Color scheme for the pie chart
  const COLORS = [
    "#0047AB", // Primary blue
    "#2E5984", // Secondary blue
    "#4682B4", // Steel blue
    "#6495ED", // Cornflower blue
    "#1E90FF", // Dodger blue
    "#87CEEB", // Sky blue
    "#ADD8E6", // Light blue
  ];
  
  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border rounded shadow-sm">
          <p className="font-medium">{payload[0].name}</p>
          <p className="text-estimator-blue">{formatCurrency(payload[0].value)}</p>
          <p className="text-gray-500 text-xs">
            {((payload[0].value / estimate.totalCost) * 100).toFixed(1)}% of total
          </p>
        </div>
      );
    }
    return null;
  };
  
  return (
    <div className="chart-container h-[400px]">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={filteredData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            fill="#8884d8"
            paddingAngle={2}
            dataKey="value"
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
          >
            {filteredData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CostBreakdownPieChart;
