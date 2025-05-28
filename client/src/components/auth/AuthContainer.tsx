
import React, { useState } from "react";
import LoginForm from "./LoginForm";
import RegisterForm from "./RegisterForm";
import { useNavigate } from "react-router-dom";

const AuthContainer: React.FC = () => {
  const [showLogin, setShowLogin] = useState(true);
  const navigate = useNavigate();
  
  const handleAuthSuccess = () => {
    navigate("/dashboard");
  };
  
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-estimator-gray-light p-4">
      <div className="w-full max-w-md mb-8 text-center">
        <h1 className="text-4xl font-bold text-estimator-blue mb-2">Project Cost Estimator</h1>
        <p className="text-gray-600">
          Get accurate cost estimates for your projects in seconds
        </p>
      </div>
      
      {showLogin ? (
        <LoginForm
          onSuccess={handleAuthSuccess}
          onRegisterClick={() => setShowLogin(false)}
        />
      ) : (
        <RegisterForm
          onSuccess={handleAuthSuccess}
          onLoginClick={() => setShowLogin(true)}
        />
      )}
    </div>
  );
};

export default AuthContainer;
