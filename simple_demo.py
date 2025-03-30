"""
Simple Demo Script for the Traffic Control System.
This script runs a basic demonstration of the traffic control system without requiring TensorFlow or OpenCV.
"""

import logging
import time
import random
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("SimpleDemo")

def setup_directories():
    """Set up necessary directories for the demo."""
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)

def simple_demo():
    """Run a simple traffic control system demo."""
    try:
        logger.info("Setting up directories...")
        setup_directories()

        logger.info("Importing required modules...")
        from modules.integration.system_integrator import SystemIntegrator, SystemConfig
        from modules.integration.event_manager import EventManager, EventPriority

        logger.info("Creating system configuration...")
        system_config = SystemConfig(
            update_interval=0.5,
            max_concurrent_tasks=2,
            log_level="INFO",
            event_manager_workers=1
        )
        
        logger.info("Initializing system integrator...")
        system = SystemIntegrator(system_config)
        
        logger.info("Starting system...")
        system.start()
        
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
        
        # Run simulation for 30 seconds
        logger.info("Simulating traffic for 30 seconds... (Press Ctrl+C to stop)")
        try:
            start_time = time.time()
            while time.time() - start_time < 30:
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
                        logger.info(f"Emergency vehicle detected: {event_data['type']} with {event_data['priority']} priority")
                    elif event_type == "public_transport":
                        event_data = {
                            "vehicle_id": f"bus_{random.randint(100, 999)}",
                            "route": f"Route-{random.randint(1, 10)}",
                            "passengers": random.randint(5, 50),
                            "behind_schedule": random.choice([True, False])
                        }
                        logger.info(f"Public transport {event_data['vehicle_id']} on {event_data['route']} with {event_data['passengers']} passengers")
                    elif event_type == "pedestrian":
                        event_data = {
                            "crossing_id": f"crossing_{random.randint(1, 10)}",
                            "waiting_count": random.randint(1, 10)
                        }
                        logger.info(f"Pedestrian crossing {event_data['crossing_id']} with {event_data['waiting_count']} waiting")
                    else:  # weather
                        event_data = {
                            "condition": random.choice(["rain", "snow", "fog", "clear"]),
                            "severity": random.choice(["light", "moderate", "severe"]),
                            "visibility": random.randint(30, 100)
                        }
                        logger.info(f"Weather condition: {event_data['severity']} {event_data['condition']} with {event_data['visibility']}% visibility")
                    
                    system.add_event(
                        event_type=event_type,
                        data=event_data
                    )
                
                # Display system status every 5 seconds
                elapsed = time.time() - start_time
                if int(elapsed) % 5 == 0 and int(elapsed) > 0:
                    light_statuses = [f"{light_id}: {system.get_traffic_light_state(light_id)['phase']}" for light_id in traffic_lights]
                    logger.info(f"Traffic light status at {int(elapsed)}s: {', '.join(light_statuses)}")
                
                # Sleep a bit
                time.sleep(0.5)
        
        except KeyboardInterrupt:
            logger.info("Demo interrupted by user.")
        
        logger.info("Stopping system...")
        system.stop()
        
        logger.info("Demo completed successfully.")
        return 0
        
    except Exception as e:
        logger.error(f"Error in simple demo: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(simple_demo()) 