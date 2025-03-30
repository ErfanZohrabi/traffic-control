"""
Simple test script for the Traffic Control System.
"""

import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("SimpleTest")

def main():
    """Run simple system test."""
    try:
        logger.info("Importing core modules...")
        from modules.integration.system_integrator import SystemIntegrator, SystemConfig
        
        logger.info("Creating system configuration...")
        config = SystemConfig(
            update_interval=1.0,
            max_concurrent_tasks=2,
            log_level="INFO",
            event_manager_workers=1
        )
        
        logger.info("Initializing system integrator...")
        system = SystemIntegrator(config)
        
        logger.info("Starting system...")
        success = system.start()
        
        if not success:
            logger.error("Failed to start the system")
            return 1
            
        logger.info("System running.")
        
        # Register a traffic light
        light_id = "test_intersection"
        initial_state = {
            "id": light_id,
            "phase": "red",
            "density": 0.2,
            "vehicle_count": 0,
            "active": True
        }
        
        logger.info(f"Registering traffic light: {light_id}")
        system.register_traffic_light(light_id, initial_state)
        
        # Wait a moment
        time.sleep(2)
        
        # Update the traffic light
        logger.info(f"Updating traffic light: {light_id}")
        system.update_traffic_light(light_id, {
            "phase": "green",
            "density": 0.5,
            "vehicle_count": 25
        })
        
        # Get the traffic light state
        time.sleep(1)
        light_state = system.get_traffic_light_state(light_id)
        logger.info(f"Traffic light state: {light_state}")
        
        # Get system status
        system_status = system.get_system_status()
        logger.info(f"System status: {system_status}")
        
        # Test event publishing
        event_id = system.add_event(
            event_type="test_event",
            data={"message": "This is a test event"}
        )
        logger.info(f"Published test event with ID: {event_id}")
        
        # Wait a moment for processing
        time.sleep(2)
        
        # Get current module health
        module_health = system.get_module_health()
        logger.info(f"Module health: {module_health}")
        
        logger.info("Stopping system...")
        system.stop()
        
        logger.info("Test completed successfully.")
        return 0
        
    except Exception as e:
        logger.error(f"Error in simple test: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main()) 