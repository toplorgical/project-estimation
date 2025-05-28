
import React from "react";
import { CostEstimate } from "@/types";
import { formatCurrency } from "@/lib/utils";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

interface CostBreakdownTableProps {
  estimate: CostEstimate;
}

const CostBreakdownTable: React.FC<CostBreakdownTableProps> = ({ estimate }) => {
  const { breakdown } = estimate;
  
  return (
    <Accordion type="single" collapsible className="space-y-4">
      {/* Labor Costs */}
      <AccordionItem value="labor" className="border rounded-lg">
        <AccordionTrigger className="px-4 py-2 hover:no-underline">
          <div className="flex justify-between items-center w-full">
            <span>Labor Costs</span>
            <span className="font-semibold">{formatCurrency(estimate.laborCost)}</span>
          </div>
        </AccordionTrigger>
        <AccordionContent className="px-4">
          <Table>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Skilled Labor</TableCell>
                <TableCell className="text-right">{formatCurrency(breakdown.labor.skilled)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Unskilled Labor</TableCell>
                <TableCell className="text-right">{formatCurrency(breakdown.labor.unskilled)}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </AccordionContent>
      </AccordionItem>
      
      {/* Material Costs */}
      <AccordionItem value="materials" className="border rounded-lg">
        <AccordionTrigger className="px-4 py-2 hover:no-underline">
          <div className="flex justify-between items-center w-full">
            <span>Material Costs</span>
            <span className="font-semibold">{formatCurrency(estimate.materialCost)}</span>
          </div>
        </AccordionTrigger>
        <AccordionContent className="px-4">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Material</TableHead>
                <TableHead className="w-24">Quantity</TableHead>
                <TableHead className="text-right w-32">Unit Cost</TableHead>
                <TableHead className="text-right w-32">Total</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {breakdown.materials.items.map((item, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">{item.name}</TableCell>
                  <TableCell>{item.quantity}</TableCell>
                  <TableCell className="text-right">{formatCurrency(item.unitCost)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(item.totalCost)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </AccordionContent>
      </AccordionItem>
      
      {/* Equipment Costs */}
      <AccordionItem value="equipment" className="border rounded-lg">
        <AccordionTrigger className="px-4 py-2 hover:no-underline">
          <div className="flex justify-between items-center w-full">
            <span>Equipment Costs</span>
            <span className="font-semibold">{formatCurrency(estimate.equipmentCost)}</span>
          </div>
        </AccordionTrigger>
        <AccordionContent className="px-4">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Equipment</TableHead>
                <TableHead className="w-24">Quantity</TableHead>
                <TableHead className="text-right w-32">Unit Cost</TableHead>
                <TableHead className="text-right w-32">Total</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {breakdown.equipment.items.map((item, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">{item.name}</TableCell>
                  <TableCell>{item.quantity}</TableCell>
                  <TableCell className="text-right">{formatCurrency(item.unitCost)}</TableCell>
                  <TableCell className="text-right">{formatCurrency(item.totalCost)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <div className="mt-4 space-y-2">
            <div className="flex justify-between text-sm">
              <span>Rental</span>
              <span>{formatCurrency(breakdown.equipment.rental)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Maintenance</span>
              <span>{formatCurrency(breakdown.equipment.maintenance)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Purchase</span>
              <span>{formatCurrency(breakdown.equipment.purchase)}</span>
            </div>
          </div>
        </AccordionContent>
      </AccordionItem>
      
      {/* Utilities Costs */}
      <AccordionItem value="utilities" className="border rounded-lg">
        <AccordionTrigger className="px-4 py-2 hover:no-underline">
          <div className="flex justify-between items-center w-full">
            <span>Utilities Costs</span>
            <span className="font-semibold">{formatCurrency(estimate.utilitiesCost)}</span>
          </div>
        </AccordionTrigger>
        <AccordionContent className="px-4">
          <Table>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Power</TableCell>
                <TableCell className="text-right">{formatCurrency(breakdown.utilities.power)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Water</TableCell>
                <TableCell className="text-right">{formatCurrency(breakdown.utilities.water)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Fuel</TableCell>
                <TableCell className="text-right">{formatCurrency(breakdown.utilities.fuel)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Communication</TableCell>
                <TableCell className="text-right">{formatCurrency(breakdown.utilities.communication)}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </AccordionContent>
      </AccordionItem>
      
      {/* Transportation Costs */}
      <AccordionItem value="transportation" className="border rounded-lg">
        <AccordionTrigger className="px-4 py-2 hover:no-underline">
          <div className="flex justify-between items-center w-full">
            <span>Transportation Costs</span>
            <span className="font-semibold">{formatCurrency(estimate.transportationCost)}</span>
          </div>
        </AccordionTrigger>
        <AccordionContent className="px-4">
          <Table>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Labor Transportation</TableCell>
                <TableCell className="text-right">{formatCurrency(breakdown.transportation.labor)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Materials Transportation</TableCell>
                <TableCell className="text-right">{formatCurrency(breakdown.transportation.materials)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Equipment Transportation</TableCell>
                <TableCell className="text-right">{formatCurrency(breakdown.transportation.equipment)}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </AccordionContent>
      </AccordionItem>
      
      {/* Regulatory Costs */}
      <AccordionItem value="regulatory" className="border rounded-lg">
        <AccordionTrigger className="px-4 py-2 hover:no-underline">
          <div className="flex justify-between items-center w-full">
            <span>Regulatory Costs</span>
            <span className="font-semibold">{formatCurrency(estimate.regulatoryCost)}</span>
          </div>
        </AccordionTrigger>
        <AccordionContent className="px-4">
          <Table>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Permits</TableCell>
                <TableCell className="text-right">{formatCurrency(breakdown.regulatory.permits)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Inspections</TableCell>
                <TableCell className="text-right">{formatCurrency(breakdown.regulatory.inspections)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Compliance</TableCell>
                <TableCell className="text-right">{formatCurrency(breakdown.regulatory.compliance)}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </AccordionContent>
      </AccordionItem>
      
      {/* Overhead Costs */}
      <AccordionItem value="overhead" className="border rounded-lg">
        <AccordionTrigger className="px-4 py-2 hover:no-underline">
          <div className="flex justify-between items-center w-full">
            <span>Overhead Costs</span>
            <span className="font-semibold">{formatCurrency(estimate.overheadCost)}</span>
          </div>
        </AccordionTrigger>
        <AccordionContent className="px-4">
          <Table>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Management</TableCell>
                <TableCell className="text-right">{formatCurrency(breakdown.overhead.management)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Insurance</TableCell>
                <TableCell className="text-right">{formatCurrency(breakdown.overhead.insurance)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Safety</TableCell>
                <TableCell className="text-right">{formatCurrency(breakdown.overhead.safety)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Miscellaneous</TableCell>
                <TableCell className="text-right">{formatCurrency(breakdown.overhead.miscellaneous)}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
};

export default CostBreakdownTable;
