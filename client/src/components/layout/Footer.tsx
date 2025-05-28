
import React from "react";

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-gray-100 py-6 border-t">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-lg font-semibold mb-2 text-estimator-blue">Project Cost Estimator</h3>
            <p className="text-sm text-gray-600">
              Get accurate cost estimates for your projects in seconds using our advanced 
              estimation technology.
            </p>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-2 text-estimator-blue">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-sm text-gray-600 hover:text-estimator-blue">
                  About Us
                </a>
              </li>
              <li>
                <a href="#" className="text-sm text-gray-600 hover:text-estimator-blue">
                  Pricing
                </a>
              </li>
              <li>
                <a href="#" className="text-sm text-gray-600 hover:text-estimator-blue">
                  Support
                </a>
              </li>
              <li>
                <a href="#" className="text-sm text-gray-600 hover:text-estimator-blue">
                  Contact
                </a>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold mb-2 text-estimator-blue">Contact Us</h3>
            <p className="text-sm text-gray-600">
              Have questions about our estimator? Contact our team for assistance.
            </p>
            <a
              href="mailto:support@projectcostestimator.com"
              className="inline-block mt-2 text-sm text-estimator-blue hover:underline"
            >
              support@projectcostestimator.com
            </a>
          </div>
        </div>
        
        <div className="mt-8 pt-4 border-t border-gray-200">
          <p className="text-sm text-center text-gray-600">
            © {currentYear} Project Cost Estimator. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
