import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error
import numpy as np
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ProjectCostEstimator:
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.model_path = os.path.join(settings.BASE_DIR, 'estimation', 'models', 'project_cost_model.joblib')
        self.preprocessor_path = os.path.join(settings.BASE_DIR, 'estimation', 'models', 'preprocessor.joblib')
        self.load_model()

    def load_model(self):
        """Load the trained model and preprocessor if they exist"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.preprocessor_path):
                self.model = joblib.load(self.model_path)
                self.preprocessor = joblib.load(self.preprocessor_path)
                logger.info("Successfully loaded trained model and preprocessor")
            else:
                logger.warning("No trained model found. A new model will be trained when data is available.")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self.model = None
            self.preprocessor = None

    def train_model(self, data):
        """
        Train the model with historical project data
        Args:
            data: DataFrame with columns ['sector', 'project_type', 'project_location', 'project_size', 'actual_cost']
        """
        try:
            if data.empty or len(data) < 10:
                logger.warning("Insufficient data for training. At least 10 samples required.")
                return False

            # Preprocess data
            X = data[['sector', 'project_type', 'project_location', 'project_size']]
            y = data['actual_cost']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Define preprocessing for categorical columns
            categorical_features = ['sector', 'project_type', 'project_location']
            categorical_transformer = OneHotEncoder(handle_unknown='ignore')
            
            preprocessor = ColumnTransformer(
                transformers=[
                    ('cat', categorical_transformer, categorical_features)
                ],
                remainder='passthrough'
            )
            
            # Create pipeline
            pipeline = Pipeline([
                ('preprocessor', preprocessor),
                ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
            ])
            
            # Train model
            pipeline.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = pipeline.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            logger.info(f"Model trained with MAE: {mae}")
            
            # Save model and preprocessor
            self.model = pipeline.named_steps['regressor']
            self.preprocessor = pipeline.named_steps['preprocessor']
            
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.preprocessor, self.preprocessor_path)
            
            return True
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return False

    def predict_cost(self, sector, project_type, project_location, project_size):
        """
        Predict project cost based on input features
        Returns:
            tuple: (predicted_cost, confidence_score)
        """
        try:
            if not self.model or not self.preprocessor:
                logger.warning("Model not trained. Cannot make predictions.")
                return None, 0.0
            
            # Create input DataFrame
            input_data = pd.DataFrame({
                'sector': [sector],
                'project_type': [project_type],
                'project_location': [project_location],
                'project_size': [project_size]
            })
            
            # Preprocess input
            X = self.preprocessor.transform(input_data)
            
            # Make prediction
            prediction = self.model.predict(X)[0]
            
            # Calculate confidence (simplified - in reality would need more sophisticated approach)
            trees_predictions = [tree.predict(X)[0] for tree in self.model.estimators_]
            std = np.std(trees_predictions)
            confidence = max(0, 1 - (std / prediction)) if prediction != 0 else 0.5
            
            return prediction, confidence
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            return None, 0.0