#!/usr/bin/env python3
"""
Test script for the Traffic Control System.
This script initializes and runs the system in simulation mode.
"""

import logging
import os
import sys
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from modules.integration.system_integrator import SystemIntegrator, SystemConfig
from modules.simulation.simulation_controller import SimulationController, SimulationConfig
from modules.ml_prediction.prediction_controller import PredictionController, PredictionConfig
from modules.dashboard.dashboard_controller import DashboardController, DashboardConfig

def setup_test_logging():
    """Set up logging for the test."""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/test_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('TestTrafficSystem')

def main():
    """Main test function."""
    logger = setup_test_logging()
    logger.info("Starting Traffic Control System Test")
    
    try:
        # Create configurations with test values
        sim_config = SimulationConfig(
            timestep=0.1,
            map_size=(1000, 1000),
            num_traffic_lights=5,
            num_vehicles=20,
            vehicle_spawn_rate=0.5,
            weather_change_prob=0.1,
            simulation_duration=60,  # 60 seconds for test
            real_time_factor=5.0,    # Run 5x faster
        )
        
        prediction_config = PredictionConfig(
            prediction_horizon=10,
            update_interval=5,
            model_type="RandomForest",
            default_window_size=30,
            min_samples_for_training=10,
        )
        
        dashboard_config = DashboardConfig(
            refresh_interval=1,
            history_window=30,
            export_path="./data/exports",
            map_center=(45.0, 9.0),
            map_zoom=13,
        )
        
        system_config = SystemConfig()  # Default config for system
        
        # Initialize controllers
        logger.info("Initializing controllers...")
        simulation = SimulationController(sim_config)
        prediction = PredictionController(prediction_config)
        dashboard = DashboardController(dashboard_config)
        system = SystemIntegrator(system_config)
        
        # Start simulation
        logger.info("Starting simulation...")
        simulation.start_simulation()
        
        # Run test for the specified duration
        logger.info(f"Running test for {sim_config.simulation_duration/sim_config.real_time_factor} seconds...")
        
        start_time = time.time()
        end_time = start_time + (sim_config.simulation_duration / sim_config.real_time_factor)
        
        # Main test loop
        while time.time() < end_time and simulation.simulation_running:
            # Get traffic data from simulation
            traffic_data = simulation.get_traffic_data()
            
            # Log some traffic metrics
            if traffic_data:
                for light_id, data in traffic_data.items():
                    logger.info(f"Traffic Light {light_id}: {data.get('vehicle_count', 0)} vehicles, "
                               f"Density: {data.get('density', 0):.2f}, "
                               f"Avg Speed: {data.get('avg_speed', 0):.2f}")
                
                # Add data to prediction model
                for light_id, data in traffic_data.items():
                    prediction.add_historical_data(light_id, data)
                
                # Make predictions after we have enough data
                for light_id in traffic_data.keys():
                    if prediction.has_enough_data(light_id):
                        predictions = prediction.predict(light_id, traffic_data[light_id])
                        if predictions:
                            logger.info(f"Prediction for Light {light_id} (5 min): "
                                      f"vehicles: {predictions.get('vehicle_count_5min', 'N/A')}, "
                                      f"density: {predictions.get('density_5min', 'N/A')}")
            
            # Process any alerts from the system
            alerts = simulation.get_alerts()
            for alert in alerts:
                logger.info(f"ALERT: {alert['type']} - {alert['message']}")
            
            # Wait before next iteration
            time.sleep(0.2)  # 5 updates per second
        
        # Stop simulation
        simulation.stop_simulation()
        
        # Log test summary
        actual_duration = time.time() - start_time
        logger.info(f"Test completed in {actual_duration:.2f} seconds")
        logger.info(f"Simulation statistics: {simulation.get_statistics()}")
        
        # Optional: Save simulation data for analysis
        simulation.export_data("./data/test_results.json")
        
        logger.info("Test completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error in test execution: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 