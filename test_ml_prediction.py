"""
Test script for the Traffic ML Prediction Module.
"""

import logging
import time
import random
import json
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("MLPredictionTest")

def main():
    """Run ML prediction test."""
    try:
        logger.info("Importing required modules...")
        from modules.integration.system_integrator import SystemIntegrator, SystemConfig
        from modules.ml_prediction.prediction_controller import PredictionController, PredictionConfig
        
        # Create data directory
        os.makedirs("data/models", exist_ok=True)
        
        # Create ML prediction configuration
        ml_config = PredictionConfig(
            model_path="data/models",
            prediction_interval=10,  # 10 seconds between predictions for testing
            prediction_horizon=60,   # 1 minute ahead for testing
            forecasting_method="arima",
            min_samples_for_training=20,  # Lower threshold for testing
            enable_anomaly_detection=True,
            anomaly_threshold=2.0
        )
        
        # Create system configuration
        system_config = SystemConfig(
            update_interval=0.5,
            max_concurrent_tasks=2,
            log_level="INFO",
            event_manager_workers=1
        )
        
        logger.info("Initializing system integrator...")
        system = SystemIntegrator(system_config)
        
        logger.info("Registering ML prediction module...")
        ml_prediction = PredictionController(ml_config)
        system.register_module('ml_prediction', ml_prediction)
        
        logger.info("Starting system...")
        system.start()
        
        # Register a traffic light
        light_id = "test_intersection"
        initial_state = {
            "id": light_id,
            "phase": "red",
            "density": 0.2,
            "vehicle_count": 20,
            "active": True
        }
        
        system.register_traffic_light(light_id, initial_state)
        logger.info(f"Registered traffic light: {light_id}")
        
        # Generate training data with traffic patterns
        logger.info("Generating training data...")
        
        # Simulate a full day of data with rush hour patterns
        simulation_hours = 24
        
        # Start time (24 hours ago)
        start_time = datetime.now() - timedelta(hours=simulation_hours)
        
        for hour in range(simulation_hours):
            current_time = start_time + timedelta(hours=hour)
            
            # Different densities based on time of day
            base_density = 0.2  # Default
            
            # Morning rush (7-9 AM)
            if 7 <= current_time.hour < 9:
                base_density = 0.7
            # Evening rush (4-7 PM)
            elif 16 <= current_time.hour < 19:
                base_density = 0.8
            # Night time (11 PM - 5 AM)
            elif current_time.hour < 5 or current_time.hour >= 23:
                base_density = 0.1
            
            # Generate multiple data points per hour with some noise
            for minute in range(0, 60, 5):  # Every 5 minutes
                # Add some random variation
                density = base_density + random.uniform(-0.1, 0.1)
                density = max(0.05, min(0.95, density))
                
                vehicle_count = int(density * 100)
                
                # Create traffic update
                data = {
                    "light_id": light_id,
                    "density": density,
                    "vehicle_count": vehicle_count,
                    "average_speed": max(5, 60 * (1 - density)),
                    "timestamp": (current_time + timedelta(minutes=minute)).isoformat()
                }
                
                # Add to ML prediction data store
                ml_prediction._store_traffic_data(light_id, data)
                
                # Also publish as event
                system.add_event(
                    event_type="traffic_update",
                    data=data
                )
        
        logger.info(f"Generated {simulation_hours * 12} training data points")
        
        # Wait for model training
        logger.info("Waiting for model training...")
        time.sleep(5)
        
        # Force training
        if light_id in ml_prediction.traffic_data:
            ml_prediction._train_model(light_id, ml_prediction.traffic_data[light_id])
            logger.info("Model training completed")
        
        # Generate a prediction
        prediction = ml_prediction._generate_prediction(light_id)
        
        if prediction:
            logger.info("Prediction generated successfully")
            logger.info(f"Prediction method: {prediction['method']}")
            logger.info(f"Number of prediction points: {len(prediction['points'])}")
            
            # Display prediction points
            logger.info("Prediction points:")
            for i, point in enumerate(prediction['points'][:5]):  # Show first 5 points
                logger.info(f"  Point {i+1}: Density: {point['density']:.2f}, Vehicles: {point['vehicle_count']}, Confidence: {point['confidence']:.2f}")
            
            # Create a visualization
            try:
                # Create plots directory
                os.makedirs("data/plots", exist_ok=True)
                
                # Extract data for plotting
                timestamps = [datetime.fromisoformat(p["timestamp"]) for p in prediction["points"]]
                densities = [p["density"] for p in prediction["points"]]
                vehicle_counts = [p["vehicle_count"] for p in prediction["points"]]
                
                # Create figure with two subplots
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
                
                # Plot density prediction
                ax1.plot(timestamps, densities, 'b-', marker='o')
                ax1.set_title(f"Traffic Density Prediction for {light_id}")
                ax1.set_ylabel("Density")
                ax1.set_ylim(0, 1)
                ax1.grid(True)
                
                # Plot vehicle count prediction
                ax2.plot(timestamps, vehicle_counts, 'r-', marker='x')
                ax2.set_title(f"Vehicle Count Prediction for {light_id}")
                ax2.set_ylabel("Vehicle Count")
                ax2.set_xlabel("Time")
                ax2.grid(True)
                
                # Format time axis
                fig.autofmt_xdate()
                
                # Save figure
                plt.tight_layout()
                fig.savefig("data/plots/prediction_visualization.png")
                logger.info("Prediction visualization saved to data/plots/prediction_visualization.png")
                
            except Exception as e:
                logger.error(f"Error creating visualization: {e}")
        else:
            logger.warning("Failed to generate prediction")
        
        # Test anomaly detection
        logger.info("Testing anomaly detection...")
        
        # Generate normal traffic update
        normal_data = {
            "light_id": light_id,
            "density": 0.3,
            "vehicle_count": 30,
            "timestamp": datetime.now().isoformat()
        }
        
        # Process normal data
        anomaly = ml_prediction._detect_anomaly(light_id, normal_data)
        logger.info(f"Normal traffic data anomaly detection: {anomaly is not None}")
        
        # Generate anomalous traffic update (very high density)
        anomaly_data = {
            "light_id": light_id,
            "density": 0.95,  # Very high
            "vehicle_count": 95,
            "timestamp": datetime.now().isoformat()
        }
        
        # Process anomalous data
        anomaly = ml_prediction._detect_anomaly(light_id, anomaly_data)
        
        if anomaly:
            logger.info("Anomaly detected successfully")
            logger.info(f"Anomaly severity: {anomaly['severity']}")
            logger.info(f"Density z-score: {anomaly['density']['z_score']:.2f}")
            logger.info(f"Vehicle count z-score: {anomaly['vehicle_count']['z_score']:.2f}")
        else:
            logger.warning("Failed to detect anomaly in anomalous data")
        
        # Run simulation and predictions for a while
        logger.info("Running real-time simulation for 30 seconds...")
        
        # Get current hour to use appropriate base density
        current_hour = datetime.now().hour
        
        # Determine base density based on time of day
        if 7 <= current_hour < 9:
            base_density = 0.7  # Morning rush
        elif 16 <= current_hour < 19:
            base_density = 0.8  # Evening rush
        elif current_hour < 5 or current_hour >= 23:
            base_density = 0.1  # Night
        else:
            base_density = 0.4  # Regular daytime
        
        try:
            start_time = time.time()
            while time.time() - start_time < 30:  # Run for 30 seconds
                # Generate traffic update with some randomness
                density = base_density + random.uniform(-0.1, 0.1)
                density = max(0.05, min(0.95, density))
                
                # Occasionally introduce anomalies
                if random.random() < 0.1:  # 10% chance
                    if random.random() < 0.5:
                        # High density anomaly
                        density = 0.9 + random.uniform(0, 0.05)
                        logger.info("Introducing high density anomaly")
                    else:
                        # Low density anomaly
                        density = 0.05 + random.uniform(0, 0.05)
                        logger.info("Introducing low density anomaly")
                
                vehicle_count = int(density * 100)
                
                # Update traffic light
                system.update_traffic_light(light_id, {
                    "density": density,
                    "vehicle_count": vehicle_count
                })
                
                # Also publish as event
                system.add_event(
                    event_type="traffic_update",
                    data={
                        "light_id": light_id,
                        "density": density,
                        "vehicle_count": vehicle_count,
                        "average_speed": max(5, 60 * (1 - density))
                    }
                )
                
                # Sleep
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("Test interrupted by user")
        
        # Get final status
        status = ml_prediction.get_status()
        logger.info(f"Final ML prediction module status: {json.dumps(status, indent=2)}")
        
        # Check all predictions
        predictions = ml_prediction.predictions.get(light_id, [])
        logger.info(f"Generated {len(predictions)} predictions")
        
        # Check all anomalies
        anomalies = ml_prediction.anomalies.get(light_id, [])
        logger.info(f"Detected {len(anomalies)} anomalies")
        
        logger.info("Stopping system...")
        system.stop()
        
        logger.info("Test completed.")
        return 0
        
    except Exception as e:
        logger.error(f"Error in ML prediction test: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main()) 