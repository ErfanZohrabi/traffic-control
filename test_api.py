"""
Test script for the Traffic System API.
"""

import logging
import time
import random
import json
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("APITest")

def main():
    """Run API test."""
    try:
        logger.info("Importing required modules...")
        from modules.integration.system_integrator import SystemIntegrator, SystemConfig
        from modules.api.api_controller import APIController, APIConfig
        
        # Create API configuration
        api_config = APIConfig(
            port=5000,
            enable_cors=True,
            require_auth=False
        )
        
        # Create system configuration with API config
        system_config = SystemConfig(
            update_interval=0.5,
            max_concurrent_tasks=2,
            log_level="INFO",
            event_manager_workers=1
        )
        
        logger.info("Initializing system integrator...")
        system = SystemIntegrator(system_config)
        
        logger.info("Registering API module...")
        api = APIController(api_config)
        api.set_system_integrator(system)
        system.register_module('api', api)
        
        logger.info("Starting system...")
        system.start()
        
        logger.info("API running at http://localhost:5000")
        
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
            
            # Update API data
            api.update_data(
                system.traffic_lights,
                [],
                system.get_system_status()
            )
        
        logger.info("Wait for API to initialize...")
        time.sleep(2)
        
        # Demonstrate API usage
        logger.info("Testing API endpoints...")
        
        # Test GET /api/status
        try:
            response = requests.get("http://localhost:5000/api/status")
            logger.info(f"Status API response: {response.status_code}")
            if response.status_code == 200:
                logger.info(f"System status: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            logger.error(f"Error testing status API: {e}")
        
        # Test GET /api/traffic-lights
        try:
            response = requests.get("http://localhost:5000/api/traffic-lights")
            logger.info(f"Traffic lights API response: {response.status_code}")
            if response.status_code == 200:
                logger.info(f"Found {len(response.json())} traffic lights")
        except Exception as e:
            logger.error(f"Error testing traffic lights API: {e}")
        
        # Test PUT /api/traffic-lights/<id> - update a traffic light
        try:
            test_light = traffic_lights[0]
            update_data = {
                "phase": "green",
                "density": 0.3
            }
            
            response = requests.put(
                f"http://localhost:5000/api/traffic-lights/{test_light}",
                json=update_data
            )
            
            logger.info(f"Update traffic light API response: {response.status_code}")
            if response.status_code == 200:
                logger.info(f"Updated traffic light {test_light}")
                
                # Verify the update
                response = requests.get(f"http://localhost:5000/api/traffic-lights/{test_light}")
                if response.status_code == 200:
                    light_data = response.json()
                    logger.info(f"Traffic light {test_light} now has phase: {light_data.get('phase')}")
        except Exception as e:
            logger.error(f"Error testing traffic light update API: {e}")
        
        # Test POST /api/events - add an event
        try:
            event_data = {
                "type": "emergency",
                "data": {
                    "vehicle_id": f"ambulance_{random.randint(1000, 9999)}",
                    "location": {
                        "lat": 40.712776,
                        "lng": -74.005974
                    },
                    "priority": "high"
                }
            }
            
            response = requests.post(
                "http://localhost:5000/api/events",
                json=event_data
            )
            
            logger.info(f"Add event API response: {response.status_code}")
            if response.status_code == 200:
                logger.info(f"Added event with ID: {response.json().get('event_id')}")
        except Exception as e:
            logger.error(f"Error testing add event API: {e}")
        
        # Wait a bit for events to process
        time.sleep(2)
        
        # Test GET /api/events
        try:
            response = requests.get("http://localhost:5000/api/events")
            logger.info(f"Events API response: {response.status_code}")
            if response.status_code == 200:
                events = response.json()
                logger.info(f"Found {len(events)} events")
                if events:
                    logger.info(f"Latest event: {json.dumps(events[-1], indent=2)}")
        except Exception as e:
            logger.error(f"Error testing events API: {e}")
        
        logger.info("API test completed. Press Ctrl+C to exit...")
        
        # Keep running for a while to allow manual API testing
        try:
            for i in range(30):  # Run for 30 seconds
                # Generate some traffic updates
                if i % 5 == 0:  # Every 5 seconds
                    for light_id in traffic_lights:
                        density = random.uniform(0.1, 0.9)
                        system.update_traffic_light(light_id, {
                            "density": density,
                            "vehicle_count": int(density * 100)
                        })
                        
                        # Publish as event
                        system.add_event(
                            event_type="traffic_update",
                            data={
                                "light_id": light_id,
                                "density": density,
                                "vehicle_count": int(density * 100)
                            }
                        )
                    
                    # Update API data
                    api.update_data(
                        system.traffic_lights,
                        system.event_manager.get_event_history(limit=100),
                        system.get_system_status()
                    )
                
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Test interrupted by user.")
        
        logger.info("Stopping system...")
        system.stop()
        
        logger.info("Test completed.")
        return 0
        
    except Exception as e:
        logger.error(f"Error in API test: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main()) 