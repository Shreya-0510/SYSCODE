"""
ML Service for training and using machine learning models for powergrid predictions
"""

import os
import pandas as pd
import numpy as np
import joblib
import logging
from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import lightgbm as lgb
from sklearn.multioutput import MultiOutputRegressor
import warnings

warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class MLService:
    """
    ML Service for powergrid project predictions
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_columns = []
        self.target_columns = ['Delay_months', 'Overrun_pct', 'Total_Cost_Cr', 'Timeline_months']
        self.models_loaded = False
        
        # Production ML pipelines (priority over auto-generated models)
        self.production_pipelines = {}
        self.production_models_loaded = False
        self.pipeline_feature_names = [
            'Project_Type', 'State', 'Latitude', 'Longitude', 'Terrain', 
            'Base_Cost_Cr', 'Steel_Price_Index', 'Cement_Price_Index', 
            'Labour_Wage_RsPerDay', 'Regulatory_Delay_months', 
            'Historical_Delay_Count', 'Avg_Annual_Rainfall_cm', 
            'Vendor_Reliability', 'Material_Availability_Index', 
            'Demand_Supply_Pressure', 'Skilled_Manpower_pct', 
            'Delay_months', 'Planned_Timeline_months', 
            'Cost_per_planned_month', 'Env_Risk_Index'
        ]
        
        # Load production pipeline models on initialization
        self.load_production_pipelines()
        
        # Model configurations
        self.model_configs = {
            'cost_overrun': {
                'target': 'Overrun_pct',
                'model_type': 'regression'
            },
            'delay_prediction': {
                'target': 'Delay_months', 
                'model_type': 'regression'
            },
            'cost_prediction': {
                'target': 'Total_Cost_Cr',
                'model_type': 'regression'  
            },
            'timeline_prediction': {
                'target': 'Timeline_months',
                'model_type': 'regression'
            }
        }
    
    def load_production_pipelines(self):
        """Load production-ready ML pipeline models"""
        try:
            model_dir = os.path.join(os.path.dirname(__file__), '..', 'models', 'trained_models')
            
            pipeline_files = {
                'cost_prediction': 'cost_pipeline.pkl',
                'overrun_prediction': 'overrun_pipeline.pkl',
                'timeline_prediction': 'time_pipeline.pkl'
            }
            
            for model_name, filename in pipeline_files.items():
                model_path = os.path.join(model_dir, filename)
                if os.path.exists(model_path):
                    try:
                        self.production_pipelines[model_name] = joblib.load(model_path)
                        logger.info(f"✓ Loaded {model_name} production pipeline")
                    except Exception as e:
                        logger.error(f"✗ Failed to load {model_name} pipeline: {e}")
                else:
                    logger.warning(f"✗ Production pipeline not found: {filename}")
            
            if self.production_pipelines:
                self.production_models_loaded = True
                logger.info(f"Production pipelines ready: {list(self.production_pipelines.keys())}")
            else:
                logger.warning("No production pipelines loaded - falling back to auto-generated models")
                
        except Exception as e:
            logger.error(f"Error loading production pipelines: {str(e)}")
            self.production_models_loaded = False
    
    def load_dataset(self, dataset_path):
        """Load and preprocess the dataset"""
        try:
            logger.info(f"Loading dataset from {dataset_path}")
            df = pd.read_csv(dataset_path)
            
            # Basic data cleaning
            df = df.dropna()
            
            # Feature engineering
            df = self._feature_engineering(df)
            
            logger.info(f"Dataset loaded successfully. Shape: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            raise
    
    def _feature_engineering(self, df):
        """Perform feature engineering on the dataset"""
        # Create derived features
        df['Cost_per_Month'] = df['Base_Cost_Cr'] / df['Planned_Timeline_months']
        df['Wage_Cost_Ratio'] = df['Labour_Wage_RsPerDay'] / df['Base_Cost_Cr']
        df['Price_Volatility'] = (abs(df['Steel_Price_Index'] - 100) + abs(df['Cement_Price_Index'] - 100)) / 2
        df['Resource_Risk'] = (2 - df['Vendor_Reliability'] - df['Material_Availability_Index']) / 2
        df['Terrain_Risk_Score'] = df['Terrain'].map({
            'Plains': 1, 'Hilly': 2, 'Desert': 3, 'Coastal': 4, 'Urban': 5, 'Mountainous': 6
        })
        df['Project_Complexity'] = df['Project_Type'].map({
            'Overhead Line': 1, 'Substation': 2, 'Underground Cable': 3
        })
        
        return df
    
    def prepare_features(self, df):
        """Prepare features for training"""
        try:
            # Select feature columns
            feature_columns = [
                'Project_Type', 'Terrain', 'Base_Cost_Cr', 'Steel_Price_Index', 'Cement_Price_Index',
                'Labour_Wage_RsPerDay', 'Regulatory_Delay_months', 'Historical_Delay_Count',
                'Avg_Annual_Rainfall_cm', 'Vendor_Reliability', 'Material_Availability_Index',
                'Demand_Supply_Pressure', 'Skilled_Manpower_pct', 'Planned_Timeline_months',
                # Derived features
                'Cost_per_Month', 'Wage_Cost_Ratio', 'Price_Volatility', 'Resource_Risk',
                'Terrain_Risk_Score', 'Project_Complexity'
            ]
            
            self.feature_columns = feature_columns
            
            # Prepare feature matrix
            X = df[feature_columns].copy()
            
            # Encode categorical variables
            categorical_columns = ['Project_Type', 'Terrain', 'Demand_Supply_Pressure']
            
            for col in categorical_columns:
                if col in X.columns:
                    if col not in self.encoders:
                        self.encoders[col] = LabelEncoder()
                        X[col] = self.encoders[col].fit_transform(X[col])
                    else:
                        X[col] = self.encoders[col].transform(X[col])
            
            # Scale numerical features
            numerical_columns = [col for col in X.columns if col not in categorical_columns]
            
            if 'scaler' not in self.scalers:
                self.scalers['scaler'] = StandardScaler()
                X[numerical_columns] = self.scalers['scaler'].fit_transform(X[numerical_columns])
            else:
                X[numerical_columns] = self.scalers['scaler'].transform(X[numerical_columns])
            
            return X
            
        except Exception as e:
            logger.error(f"Error preparing features: {str(e)}")
            raise
    
    def train_models(self, dataset_path, save_models=True):
        """Train all ML models"""
        try:
            logger.info("Starting model training...")
            
            # Load and prepare data
            df = self.load_dataset(dataset_path)
            X = self.prepare_features(df)
            
            # Train individual models
            for model_name, config in self.model_configs.items():
                logger.info(f"Training {model_name} model...")
                
                target = config['target']
                y = df[target]
                
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
                
                # Train multiple algorithms and select best
                best_model = self._train_and_select_best_model(
                    X_train, X_test, y_train, y_test, model_name
                )
                
                self.models[model_name] = best_model
                
                # Evaluate model
                y_pred = best_model.predict(X_test)
                metrics = self._calculate_metrics(y_test, y_pred)
                
                logger.info(f"{model_name} model trained. Metrics: {metrics}")
            
            # Train multi-output model for comprehensive predictions
            self._train_multioutput_model(X, df)
            
            if save_models:
                self.save_models()
            
            self.models_loaded = True
            logger.info("All models trained successfully!")
            
            return True
            
        except Exception as e:
            logger.error(f"Error training models: {str(e)}")
            raise
    
    def _train_and_select_best_model(self, X_train, X_test, y_train, y_test, model_name):
        """Train multiple algorithms and select the best one"""
        
        # Define models to try
        models_to_try = {
            'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1),
            'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'XGBoost': xgb.XGBRegressor(n_estimators=100, random_state=42, n_jobs=-1),
            'LightGBM': lgb.LGBMRegressor(n_estimators=100, random_state=42, n_jobs=-1, verbose=-1)
        }
        
        best_model = None
        best_score = float('inf')
        
        for name, model in models_to_try.items():
            try:
                # Train model
                model.fit(X_train, y_train)
                
                # Predict and evaluate
                y_pred = model.predict(X_test)
                mse = mean_squared_error(y_test, y_pred)
                
                logger.info(f"{model_name} - {name}: MSE = {mse:.4f}")
                
                if mse < best_score:
                    best_score = mse
                    best_model = model
                    
            except Exception as e:
                logger.warning(f"Error training {name} for {model_name}: {str(e)}")
                continue
        
        if best_model is None:
            # Fallback to simple linear regression
            best_model = LinearRegression()
            best_model.fit(X_train, y_train)
            logger.warning(f"Using fallback LinearRegression for {model_name}")
        
        return best_model
    
    def _train_multioutput_model(self, X, df):
        """Train a multi-output model for comprehensive predictions"""
        try:
            # Prepare multi-output targets
            y_multi = df[self.target_columns]
            
            # Use RandomForest as base estimator for multi-output
            base_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
            multi_model = MultiOutputRegressor(base_model)
            
            # Train
            multi_model.fit(X, y_multi)
            
            self.models['multioutput'] = multi_model
            logger.info("Multi-output model trained successfully")
            
        except Exception as e:
            logger.error(f"Error training multi-output model: {str(e)}")
    
    def _calculate_metrics(self, y_true, y_pred):
        """Calculate evaluation metrics"""
        return {
            'mse': mean_squared_error(y_true, y_pred),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred))
        }
    
    def predict(self, features, prediction_type='all'):
        """Make predictions using your trained models"""
        try:
            # Use your 3 trained models directly
            if self.production_models_loaded and len(self.production_pipelines) > 0:
                
                # Prepare features for your models with EXACT categories expected
                features_df = pd.DataFrame([{
                    'Project_Type': str(features.get('projectType', 'Overhead Line')),  # ['Overhead Line', 'Substation', 'Underground Cable']
                    'State': str(features.get('state', 'Maharashtra')),  # ['Assam', 'Delhi', 'Gujarat', 'Karnataka', 'Maharashtra', 'Rajasthan', 'Tamil Nadu', 'Uttarakhand']
                    'Latitude': float(features.get('latitude', 19.0760)),
                    'Longitude': float(features.get('longitude', 72.8777)),
                    'Terrain': str(features.get('terrain', 'Plains')),  # ['Coastal', 'Desert', 'Hilly', 'Mountainous', 'Plains', 'Urban']
                    'Base_Cost_Cr': float(features.get('baseCost', 100.0)),
                    'Steel_Price_Index': float(features.get('steelPrice', 100.0)),
                    'Cement_Price_Index': float(features.get('cementPrice', 100.0)),
                    'Labour_Wage_RsPerDay': float(features.get('labourWage', 500.0)),
                    'Regulatory_Delay_months': float(features.get('regulatoryDelay', 2.0)),
                    'Historical_Delay_Count': float(features.get('historicalDelay', 1.0)),
                    'Avg_Annual_Rainfall_cm': float(features.get('rainfall', 120.0)),
                    'Vendor_Reliability': float(features.get('vendorReliability', 0.8)),
                    'Material_Availability_Index': float(features.get('materialAvailability', 0.8)),
                    'Demand_Supply_Pressure': str(features.get('demandSupplyPressure', 'Medium')),  # ['High', 'Low', 'Medium']
                    'Skilled_Manpower_pct': float(features.get('skilledManpower', 70.0)) / 100.0,
                    'Delay_months': float(features.get('delayMonths', 0.0)),
                    'Planned_Timeline_months': float(features.get('plannedTimeline', 24.0)),
                    'Cost_per_planned_month': float(features.get('baseCost', 100.0)) / float(features.get('plannedTimeline', 24.0)),
                    'Env_Risk_Index': float(features.get('envRisk', 0.3))
                }])
                
                # Map invalid values to valid categories
                project_type_map = {'Transmission': 'Overhead Line', 'Distribution': 'Underground Cable'}
                if features_df.loc[0, 'Project_Type'] in project_type_map:
                    features_df.loc[0, 'Project_Type'] = project_type_map[features_df.loc[0, 'Project_Type']]
                
                terrain_map = {'Plain': 'Plains', 'Hill': 'Hilly', 'Mountain': 'Mountainous'}
                if features_df.loc[0, 'Terrain'] in terrain_map:
                    features_df.loc[0, 'Terrain'] = terrain_map[features_df.loc[0, 'Terrain']]
                
                # Ensure column order matches exactly what models expect
                expected_features = [
                    'Project_Type', 'State', 'Latitude', 'Longitude', 'Terrain', 
                    'Base_Cost_Cr', 'Steel_Price_Index', 'Cement_Price_Index', 
                    'Labour_Wage_RsPerDay', 'Regulatory_Delay_months', 
                    'Historical_Delay_Count', 'Avg_Annual_Rainfall_cm', 
                    'Vendor_Reliability', 'Material_Availability_Index', 
                    'Demand_Supply_Pressure', 'Skilled_Manpower_pct', 
                    'Delay_months', 'Planned_Timeline_months', 
                    'Cost_per_planned_month', 'Env_Risk_Index'
                ]
                
                features_df = features_df[expected_features]
                
                predictions = {}
                
                # Make predictions with your 3 models
                for model_name, model in self.production_pipelines.items():
                    try:
                        pred = model.predict(features_df)[0]
                        predictions[model_name] = float(pred)
                    except Exception as e:
                        logger.error(f"Error with {model_name}: {str(e)}")
                        predictions[model_name] = 0.0
                
                return predictions
            
            # Fallback if models not loaded
            if not self.models_loaded:
                logger.warning("Models not loaded. Loading saved models...")
                self.load_models()
            
            # Prepare features
            X = self._prepare_single_prediction_features(features)
            
            predictions = {}
            
            if prediction_type == 'all':
                # Use multi-output model if available
                if 'multioutput' in self.models:
                    multi_pred = self.models['multioutput'].predict(X.reshape(1, -1))[0]
                    predictions = {
                        'delay_months': float(multi_pred[0]),
                        'cost_overrun_pct': float(multi_pred[1]),
                        'total_cost_cr': float(multi_pred[2]),
                        'timeline_months': float(multi_pred[3])
                    }
                else:
                    # Use individual models
                    for model_name in self.model_configs:
                        if model_name in self.models:
                            pred = self.models[model_name].predict(X.reshape(1, -1))[0]
                            predictions[model_name] = float(pred)
            else:
                # Single prediction
                if prediction_type in self.models:
                    pred = self.models[prediction_type].predict(X.reshape(1, -1))[0]
                    predictions[prediction_type] = float(pred)
            
            # Add risk assessment
            predictions['risk_assessment'] = self._assess_risk(predictions)
            predictions['confidence_score'] = self._calculate_confidence(features)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            raise
    
    def _predict_with_production_pipelines(self, features, prediction_type='all'):
        """Make predictions using production-ready ML pipelines"""
        try:
            # Prepare features for production pipelines
            features_df = self._prepare_production_features(features)
            
            predictions = {}
            
            if prediction_type == 'all':
                # Use all available production pipelines
                for model_name, pipeline in self.production_pipelines.items():
                    try:
                        prediction = pipeline.predict(features_df)[0]
                        predictions[model_name] = float(prediction)
                    except Exception as e:
                        logger.error(f"Error with {model_name} pipeline: {e}")
                        predictions[model_name] = 0.0
            else:
                # Single prediction type
                if prediction_type in self.production_pipelines:
                    try:
                        prediction = self.production_pipelines[prediction_type].predict(features_df)[0]
                        predictions[prediction_type] = float(prediction)
                    except Exception as e:
                        logger.error(f"Error with {prediction_type} pipeline: {e}")
                        predictions[prediction_type] = 0.0
            
            # Add enhanced risk assessment for production models
            predictions['risk_assessment'] = self._assess_production_risk(predictions, features)
            predictions['confidence_score'] = self._calculate_production_confidence(features)
            predictions['model_source'] = 'production_pipeline'
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error making production pipeline prediction: {str(e)}")
            raise
    
    def _prepare_production_features(self, project_data):
        """Convert frontend data to format expected by production ML pipelines"""
        # Map frontend fields to production pipeline features with intelligent defaults
        
        features = {
            # Core project details (ensure proper data types)
            'Project_Type': str(project_data.get('projectType', 'Transmission')),
            'State': str(project_data.get('state', 'Maharashtra')),
            'Latitude': float(project_data.get('latitude', 19.0760)),  # Mumbai default
            'Longitude': float(project_data.get('longitude', 72.8777)),
            'Terrain': str(project_data.get('terrain', 'Plain')),
            
            # Cost factors (ensure all are float)
            'Base_Cost_Cr': float(project_data.get('baseCost', 100.0)),
            'Steel_Price_Index': float(project_data.get('steelPrice', 100.0)),
            'Cement_Price_Index': float(project_data.get('cementPrice', 100.0)),
            'Labour_Wage_RsPerDay': float(project_data.get('labourWage', 500.0)),
            
            # Delay factors (ensure all are float)
            'Regulatory_Delay_months': float(project_data.get('regulatoryDelay', 2.0)),
            'Historical_Delay_Count': float(project_data.get('historicalDelay', 1.0)),
            'Delay_months': float(project_data.get('delayMonths', 0.0)),
            
            # Environmental factors (ensure all are float)
            'Avg_Annual_Rainfall_cm': float(project_data.get('rainfall', 120.0)),
            'Env_Risk_Index': float(project_data.get('envRisk', 0.3)),
            
            # Operational factors (ensure all are float)
            'Vendor_Reliability': float(project_data.get('vendorReliability', 0.8)),
            'Material_Availability_Index': float(project_data.get('materialAvailability', 0.8)),
            'Demand_Supply_Pressure': float(project_data.get('demandSupplyPressure', 0.5)),
            'Skilled_Manpower_pct': float(project_data.get('skilledManpower', 70.0)) / 100.0,  # Convert to decimal
            
            # Timeline factors (ensure all are float)
            'Planned_Timeline_months': float(project_data.get('plannedTimeline', 24.0)),
            'Cost_per_planned_month': float(project_data.get('baseCost', 100.0)) / float(project_data.get('plannedTimeline', 24.0))
        }
        
        # Create DataFrame and ensure all columns match expected dtypes
        df = pd.DataFrame([features])
        
        # Debug: Print dtypes and check for any object/string columns that should be numeric
        print("Feature dtypes:")
        for col, dtype in df.dtypes.items():
            if col in ['Project_Type', 'State', 'Terrain']:
                # These should remain as strings/objects
                continue
            elif dtype == 'object':
                print(f"  WARNING: {col} is object type, converting to float")
                df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                print(f"  {col}: {dtype}")
        
        return df
    
    def _prepare_single_prediction_features(self, features):
        """Prepare features for a single prediction"""
        try:
            # Create a DataFrame with the features
            df = pd.DataFrame([features])
            
            # Feature engineering
            df = self._feature_engineering(df)
            
            # Select and order features
            X = df[self.feature_columns].copy()
            
            # Encode categorical variables
            categorical_columns = ['Project_Type', 'Terrain', 'Demand_Supply_Pressure']
            
            for col in categorical_columns:
                if col in X.columns and col in self.encoders:
                    X[col] = self.encoders[col].transform(X[col])
            
            # Scale features
            numerical_columns = [col for col in X.columns if col not in categorical_columns]
            if 'scaler' in self.scalers:
                X[numerical_columns] = self.scalers['scaler'].transform(X[numerical_columns])
            
            return X.values[0]
            
        except Exception as e:
            logger.error(f"Error preparing single prediction features: {str(e)}")
            raise
    
    def _assess_risk(self, predictions):
        """Assess overall project risk based on predictions"""
        risk_score = 0
        
        # Cost overrun risk
        if predictions.get('cost_overrun_pct', 0) > 20:
            risk_score += 3
        elif predictions.get('cost_overrun_pct', 0) > 10:
            risk_score += 2
        elif predictions.get('cost_overrun_pct', 0) > 5:
            risk_score += 1
        
        # Delay risk
        if predictions.get('delay_months', 0) > 6:
            risk_score += 3
        elif predictions.get('delay_months', 0) > 3:
            risk_score += 2
        elif predictions.get('delay_months', 0) > 1:
            risk_score += 1
        
        # Risk categorization
        if risk_score >= 5:
            return 'High'
        elif risk_score >= 3:
            return 'Medium'
        else:
            return 'Low'
    
    def _calculate_confidence(self, features):
        """Calculate prediction confidence based on feature completeness and quality"""
        completeness_factors = []
        
        # Check completeness of key features
        key_features = [
            'Base_Cost_Cr', 'Vendor_Reliability', 'Material_Availability_Index',
            'Skilled_Manpower_pct', 'Planned_Timeline_months'
        ]
        
        for feature in key_features:
            if feature in features and features[feature] is not None:
                completeness_factors.append(1)
            else:
                completeness_factors.append(0)
        
        # Base confidence from completeness
        base_confidence = sum(completeness_factors) / len(completeness_factors) * 100
        
        # Adjust based on data quality
        quality_adjustments = 0
        
        # High vendor reliability increases confidence
        if features.get('Vendor_Reliability', 0) > 0.8:
            quality_adjustments += 5
        
        # High material availability increases confidence
        if features.get('Material_Availability_Index', 0) > 0.8:
            quality_adjustments += 5
        
        # Low historical delay count increases confidence
        if features.get('Historical_Delay_Count', 0) < 3:
            quality_adjustments += 5
        
        final_confidence = min(100, base_confidence + quality_adjustments)
        return round(final_confidence, 1)
    
    def _assess_production_risk(self, predictions, features):
        """Enhanced risk assessment for production pipeline predictions"""
        risk_score = 0
        risk_factors = []
        
        # Cost prediction risk assessment
        cost_pred = predictions.get('cost_prediction', 0)
        if cost_pred > 200:  # Above 200 Cr
            risk_score += 3
            risk_factors.append('High cost prediction')
        elif cost_pred > 100:
            risk_score += 2
            risk_factors.append('Medium cost prediction')
        
        # Overrun prediction risk assessment
        overrun_pred = predictions.get('overrun_prediction', 0)
        if overrun_pred > 25:  # Above 25% overrun
            risk_score += 3
            risk_factors.append('High overrun risk')
        elif overrun_pred > 10:
            risk_score += 2
            risk_factors.append('Medium overrun risk')
        
        # Timeline prediction risk assessment
        timeline_pred = predictions.get('timeline_prediction', 0)
        planned_timeline = features.get('plannedTimeline', 24)
        if timeline_pred > planned_timeline * 1.5:  # 50% longer than planned
            risk_score += 3
            risk_factors.append('Significant timeline extension')
        elif timeline_pred > planned_timeline * 1.2:  # 20% longer than planned
            risk_score += 2
            risk_factors.append('Moderate timeline extension')
        
        # Environmental and operational risks
        env_risk = features.get('envRisk', 0.3)
        if env_risk > 0.7:
            risk_score += 2
            risk_factors.append('High environmental risk')
        
        vendor_reliability = features.get('vendorReliability', 0.8)
        if vendor_reliability < 0.6:
            risk_score += 2
            risk_factors.append('Low vendor reliability')
        
        # Determine overall risk level
        if risk_score >= 6:
            risk_level = 'Critical'
        elif risk_score >= 4:
            risk_level = 'High'
        elif risk_score >= 2:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        return {
            'level': risk_level,
            'score': risk_score,
            'factors': risk_factors
        }
    
    def _calculate_production_confidence(self, features):
        """Calculate confidence score for production pipeline predictions"""
        confidence_factors = []
        
        # Data completeness assessment
        required_features = [
            'projectType', 'state', 'baseCost', 'plannedTimeline', 
            'vendorReliability', 'materialAvailability'
        ]
        
        completeness_score = 0
        for feature in required_features:
            if feature in features and features[feature] is not None:
                completeness_score += 1
        
        completeness_ratio = completeness_score / len(required_features)
        confidence_factors.append(completeness_ratio * 40)  # Max 40 points for completeness
        
        # Data quality assessment
        quality_score = 0
        
        # Vendor reliability quality
        vendor_rel = features.get('vendorReliability', 0)
        if vendor_rel >= 0.8:
            quality_score += 15
        elif vendor_rel >= 0.6:
            quality_score += 10
        elif vendor_rel >= 0.4:
            quality_score += 5
        
        # Material availability quality
        material_avail = features.get('materialAvailability', 0)
        if material_avail >= 0.8:
            quality_score += 15
        elif material_avail >= 0.6:
            quality_score += 10
        elif material_avail >= 0.4:
            quality_score += 5
        
        # Environmental risk assessment (lower risk = higher confidence)
        env_risk = features.get('envRisk', 0.3)
        if env_risk <= 0.3:
            quality_score += 10
        elif env_risk <= 0.5:
            quality_score += 5
        
        # Historical data consistency
        hist_delay = features.get('historicalDelay', 1)
        if hist_delay <= 2:
            quality_score += 10
        elif hist_delay <= 5:
            quality_score += 5
        
        confidence_factors.append(quality_score)  # Max ~55 points for quality
        
        # Geographic data precision
        if features.get('latitude') and features.get('longitude'):
            confidence_factors.append(5)  # 5 points for geo data
        
        final_confidence = min(100, sum(confidence_factors))
        return round(final_confidence, 1)
    
    def save_models(self, model_dir=None):
        """Save trained models to disk"""
        try:
            if model_dir is None:
                from app import app
                model_dir = app.config['MODEL_DIR']
            
            os.makedirs(model_dir, exist_ok=True)
            
            # Save models
            for model_name, model in self.models.items():
                model_path = os.path.join(model_dir, f'{model_name}_model.pkl')
                joblib.dump(model, model_path)
                logger.info(f"Saved {model_name} model to {model_path}")
            
            # Save scalers and encoders
            scalers_path = os.path.join(model_dir, 'scalers.pkl')
            joblib.dump(self.scalers, scalers_path)
            
            encoders_path = os.path.join(model_dir, 'encoders.pkl')
            joblib.dump(self.encoders, encoders_path)
            
            # Save feature columns
            features_path = os.path.join(model_dir, 'feature_columns.pkl')
            joblib.dump(self.feature_columns, features_path)
            
            logger.info("All models and preprocessors saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
            raise
    
    def load_models(self, model_dir=None):
        """Load trained models from disk"""
        try:
            if model_dir is None:
                from app import app
                model_dir = app.config['MODEL_DIR']
            
            if not os.path.exists(model_dir):
                logger.warning("Model directory not found. Training new models...")
                from app import app
                self.train_models(app.config['DATASET_PATH'])
                return
            
            # Load models
            for model_name in self.model_configs:
                model_path = os.path.join(model_dir, f'{model_name}_model.pkl')
                if os.path.exists(model_path):
                    self.models[model_name] = joblib.load(model_path)
                    logger.info(f"Loaded {model_name} model")
            
            # Load multi-output model if exists
            multioutput_path = os.path.join(model_dir, 'multioutput_model.pkl')
            if os.path.exists(multioutput_path):
                self.models['multioutput'] = joblib.load(multioutput_path)
                logger.info("Loaded multi-output model")
            
            # Load scalers and encoders
            scalers_path = os.path.join(model_dir, 'scalers.pkl')
            if os.path.exists(scalers_path):
                self.scalers = joblib.load(scalers_path)
            
            encoders_path = os.path.join(model_dir, 'encoders.pkl')
            if os.path.exists(encoders_path):
                self.encoders = joblib.load(encoders_path)
            
            # Load feature columns
            features_path = os.path.join(model_dir, 'feature_columns.pkl')
            if os.path.exists(features_path):
                self.feature_columns = joblib.load(features_path)
            
            self.models_loaded = True
            logger.info("All models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            # Try to train new models as fallback
            try:
                from app import app
                logger.info("Attempting to train new models as fallback...")
                self.train_models(app.config['DATASET_PATH'])
            except Exception as train_error:
                logger.error(f"Failed to train fallback models: {str(train_error)}")
                raise
    
    def get_feature_importance(self, model_name='cost_overrun'):
        """Get feature importance for a specific model"""
        try:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not found")
            
            model = self.models[model_name]
            
            if hasattr(model, 'feature_importances_'):
                importance_dict = {}
                for i, feature in enumerate(self.feature_columns):
                    importance_dict[feature] = float(model.feature_importances_[i])
                
                # Sort by importance
                sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
                return dict(sorted_importance)
            
            else:
                logger.warning(f"Model {model_name} does not support feature importance")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting feature importance: {str(e)}")
            return {}
    
    def retrain_model(self, model_name, new_data_path=None):
        """Retrain a specific model with new data"""
        try:
            logger.info(f"Retraining {model_name} model...")
            
            if new_data_path:
                df = self.load_dataset(new_data_path)
            else:
                from app import app
                df = self.load_dataset(app.config['DATASET_PATH'])
            
            X = self.prepare_features(df)
            
            if model_name in self.model_configs:
                target = self.model_configs[model_name]['target']
                y = df[target]
                
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
                
                retrained_model = self._train_and_select_best_model(
                    X_train, X_test, y_train, y_test, model_name
                )
                
                self.models[model_name] = retrained_model
                
                # Save the retrained model
                self.save_models()
                
                logger.info(f"{model_name} model retrained successfully")
                return True
            
            else:
                raise ValueError(f"Unknown model name: {model_name}")
                
        except Exception as e:
            logger.error(f"Error retraining model {model_name}: {str(e)}")
            raise
    
    def get_production_pipeline_info(self):
        """Get information about loaded production pipelines"""
        info = {
            'production_models_available': self.production_models_loaded,
            'pipelines_loaded': list(self.production_pipelines.keys()) if self.production_models_loaded else [],
            'feature_count': len(self.pipeline_feature_names),
            'required_features': self.pipeline_feature_names,
            'fallback_models': list(self.models.keys()) if self.models_loaded else [],
            'model_source': 'production_pipeline' if self.production_models_loaded else 'auto_generated'
        }
        return info
    
    def is_production_ready(self):
        """Check if production pipelines are ready for predictions"""
        return self.production_models_loaded and len(self.production_pipelines) >= 2  # At least 2 models required