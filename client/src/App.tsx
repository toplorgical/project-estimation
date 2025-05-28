
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { SubscriptionProvider } from "@/contexts/SubscriptionContext";
import { ThemeProvider } from "@/contexts/ThemeContext";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import Layout from "@/components/layout/Layout";

// Pages
import Index from "./pages/Index";
import Auth from "./pages/Auth";
import Dashboard from "./pages/Dashboard";
import NewEstimate from "./pages/NewEstimate";
import EstimateResult from "./pages/EstimateResult";
import SavedEstimates from "./pages/SavedEstimates";
import EstimateDetail from "./pages/EstimateDetail";
import Profile from "./pages/Profile";
import Subscription from "./pages/Subscription";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <ThemeProvider>
        <Toaster />
        <Sonner />
        <AuthProvider>
          <SubscriptionProvider>
            <BrowserRouter>
              <Routes>
                <Route path="/" element={<Index />} />
                <Route path="/auth" element={<Auth />} />
                
                {/* Protected Routes within Layout */}
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <Layout />
                    </ProtectedRoute>
                  }
                >
                  <Route path="dashboard" element={<Dashboard />} />
                  <Route path="new-estimate" element={<NewEstimate />} />
                  <Route path="estimate-result" element={<EstimateResult />} />
                  <Route path="estimates" element={<SavedEstimates />} />
                  <Route path="estimate/:id" element={<EstimateDetail />} />
                  <Route path="profile" element={<Profile />} />
                  <Route path="subscription" element={<Subscription />} />
                </Route>
                
                {/* 404 Route */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </BrowserRouter>
          </SubscriptionProvider>
        </AuthProvider>
      </ThemeProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
