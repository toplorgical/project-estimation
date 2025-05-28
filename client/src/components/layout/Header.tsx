
import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import ThemeToggle from "@/components/theme/ThemeToggle";

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  const handleLogout = () => {
    logout();
    navigate("/");
  };
  
  const userInitials = user?.name
    ? user.name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
    : "U";
  
  return (
    <header className="bg-background border-b border-border py-4 sticky top-0 z-10 transition-colors">
      <div className="container mx-auto px-4 flex justify-between items-center">
        <Link to="/dashboard" className="flex items-center transition-transform hover-scale">
          <span className="text-2xl font-bold text-estimator-blue animate-fade-in">
            ProjectCost
          </span>
        </Link>
        
        <nav className="hidden md:flex space-x-6">
          <Link 
            to="/dashboard" 
            className="text-foreground hover:text-estimator-blue font-medium transition-colors"
          >
            Dashboard
          </Link>
          <Link 
            to="/new-estimate" 
            className="text-foreground hover:text-estimator-blue font-medium transition-colors"
          >
            New Estimate
          </Link>
          <Link 
            to="/estimates" 
            className="text-foreground hover:text-estimator-blue font-medium transition-colors"
          >
            Saved Estimates
          </Link>
        </nav>
        
        <div className="flex items-center space-x-4">
          <ThemeToggle />
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full hover:bg-muted/50">
                <Avatar>
                  <AvatarFallback className="bg-estimator-blue text-white">
                    {userInitials}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56 animate-scale-in">
              <div className="p-2">
                <p className="text-sm font-medium leading-none">{user?.name}</p>
                <p className="text-xs text-muted-foreground mt-1">{user?.email}</p>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link to="/dashboard" className="w-full cursor-pointer">Dashboard</Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link to="/new-estimate" className="w-full cursor-pointer">New Estimate</Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link to="/estimates" className="w-full cursor-pointer">Saved Estimates</Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link to="/profile" className="w-full cursor-pointer">Profile Settings</Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout} className="text-red-600 cursor-pointer">
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
};

export default Header;
