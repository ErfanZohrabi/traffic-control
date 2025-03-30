"""
Test script for the Traffic System Dashboard.
"""

import logging
import time
import random
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("DashboardTest")

def main():
    """Run dashboard test."""
    try:
        logger.info("Importing required modules...")
        from modules.integration.system_integrator import SystemIntegrator, SystemConfig
        from modules.dashboard.dashboard_controller import DashboardController, DashboardConfig
        
        # Create dashboard configuration
        dashboard_config = DashboardConfig(
            port=8080,
            auto_open_browser=True,
            update_interval=0.5
        )
        
        # Create system configuration with dashboard config
        system_config = SystemConfig(
            update_interval=0.5,
            max_concurrent_tasks=2,
            log_level="INFO",
            event_manager_workers=1,
            dashboard_config=dashboard_config
        )
        
        logger.info("Initializing system integrator...")
        system = SystemIntegrator(system_config)
        
        logger.info("Registering dashboard module...")
        dashboard = DashboardController(dashboard_config)
        system.register_module('dashboard', dashboard)
        
        logger.info("Starting system...")
        system.start()
        
        logger.info("Dashboard running at http://localhost:8080")
        
        # Register some traffic lights
        traffic_lights = [
            "intersection_main_1",
            "intersection_main_2",
            "intersection_side_1",
            "intersection_side_2"
        ]
        
        for light_id in traffic_lights:
            initial_state = {
                "id": light_id,
                "phase": random.choice(["red", "yellow", "green"]),
                "density": random.uniform(0.1, 0.9),
                "vehicle_count": random.randint(0, 50),
                "active": True
            }
            system.register_traffic_light(light_id, initial_state)
            logger.info(f"Registered traffic light: {light_id}")
            
            # Update dashboard directly
            dashboard.update_traffic_light(light_id, initial_state)
        
        logger.info("Simulating traffic for 60 seconds... (Press Ctrl+C to stop)")
        
        # Run simulation for 60 seconds
        try:
            start_time = time.time()
            while time.time() - start_time < 60:
                # Update each light
                for light_id in traffic_lights:
                    # Randomly change light phase occasionally
                    if random.random() < 0.1:
                        phase = random.choice(["red", "yellow", "green"])
                        
                        # Update traffic light state in system
                        system.update_traffic_light(light_id, {
                            "phase": phase
                        })
                    
                    # Update traffic data
                    density = random.uniform(0.1, 0.9)
                    vehicle_count = int(density * 100)
                    
                    # Publish as traffic update event
                    system.add_event(
                        event_type="traffic_update",
                        data={
                            "light_id": light_id,
                            "density": density,
                            "vehicle_count": vehicle_count,
                            "average_speed": max(5, 60 * (1 - density))
                        }
                    )
                
                # Occasionally generate special events
                if random.random() < 0.15:
                    event_types = ["emergency", "public_transport", "pedestrian", "weather"]
                    event_type = random.choice(event_types)
                    
                    if event_type == "emergency":
                        event_data = {
                            "type": random.choice(["ambulance", "police", "fire"]),
                            "location": f"near {random.choice(traffic_lights)}",
                            "priority": random.choice(["high", "medium", "critical"])
                        }
                    elif event_type == "public_transport":
                        event_data = {
                            "vehicle_id": f"bus_{random.randint(100, 999)}",
                            "route": f"Route-{random.randint(1, 10)}",
                            "passengers": random.randint(5, 50),
                            "behind_schedule": random.choice([True, False])
                        }
                    elif event_type == "pedestrian":
                        event_data = {
                            "crossing_id": f"crossing_{random.randint(1, 10)}",
                            "waiting_count": random.randint(1, 10)
                        }
                    else:  # weather
                        event_data = {
                            "condition": random.choice(["rain", "snow", "fog", "clear"]),
                            "severity": random.choice(["light", "moderate", "severe"]),
                            "visibility": random.randint(30, 100)
                        }
                    
                    system.add_event(
                        event_type=event_type,
                        data=event_data
                    )
                    logger.info(f"Generated {event_type} event")
                
                # Sleep a bit
                time.sleep(0.5)
        
        except KeyboardInterrupt:
            logger.info("Test interrupted by user.")
        
        logger.info("Stopping system...")
        system.stop()
        
        logger.info("Test completed.")
        return 0
        
    except Exception as e:
        logger.error(f"Error in dashboard test: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main()) 