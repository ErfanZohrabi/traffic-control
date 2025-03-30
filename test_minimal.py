"""
Minimal test script for the Traffic Control System.
"""

import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("MinimalTest")

def main():
    """Run minimal system test."""
    try:
        logger.info("Importing core modules...")
        from modules.integration.system_integrator import SystemIntegrator, SystemConfig
        from modules.integration.event_manager import EventManager
        
        logger.info("Creating system configuration...")
        config = SystemConfig(
            update_interval=0.5,
            max_concurrent_tasks=2,
            log_level="DEBUG",
            event_manager_workers=1
        )
        
        logger.info("Initializing system integrator...")
        system = SystemIntegrator(config)
        
        logger.info("Starting system...")
        system.start()
        
        logger.info("System running. Press Ctrl+C to exit.")
        
        # Run for a few seconds
        try:
            for i in range(5):
                logger.info(f"System running... ({i+1}/5)")
                # Add a test event
                system.add_event(
                    event_type="test_event",
                    data={"message": f"Test event {i+1}"}
                )
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Interrupted by user.")
        
        logger.info("Stopping system...")
        system.stop()
        
        logger.info("Test completed successfully.")
        return 0
        
    except Exception as e:
        logger.error(f"Error in minimal test: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main()) 