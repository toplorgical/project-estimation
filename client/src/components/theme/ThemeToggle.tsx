
import React from "react";
import { Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/contexts/ThemeContext";

const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <Button 
      variant="ghost" 
      size="icon" 
      onClick={toggleTheme}
      className="rounded-full transition-all duration-300 hover:bg-muted"
    >
      {theme === "light" ? (
        <Sun className="h-5 w-5 transition-all duration-300 rotate-0" />
      ) : (
        <Moon className="h-5 w-5 transition-all duration-300 rotate-90" />
      )}
      <span className="sr-only">Toggle theme</span>
    </Button>
  );
};

export default ThemeToggle;
