"""
Simple test for the Event Manager.
"""

import logging
import time
import threading
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("EventManagerTest")

def event_callback(event):
    """Simple callback for events."""
    logger.info(f"Event received: {event}")

def main():
    """Test the event manager."""
    try:
        logger.info("Importing EventManager...")
        from modules.integration.event_manager import EventManager, EventPriority
        
        logger.info("Creating event manager...")
        event_manager = EventManager(worker_threads=1)
        
        logger.info("Starting event manager...")
        event_manager.start()
        
        # Subscribe to events
        logger.info("Subscribing to events...")
        event_manager.subscribe(
            subscriber_id="test_subscriber",
            event_types=["test_event"],
            callback=event_callback
        )
        
        # Publish some events
        logger.info("Publishing events...")
        for i in range(3):
            event_id = event_manager.publish(
                event_type="test_event",
                source="test_script",
                data={"message": f"Test event {i+1}", "timestamp": datetime.now().isoformat()}
            )
            logger.info(f"Published event with ID: {event_id}")
            time.sleep(1)
        
        # Wait a bit for events to be processed
        logger.info("Waiting for events to be processed...")
        time.sleep(2)
        
        # Get subscriber stats
        stats = event_manager.get_subscriber_stats()
        logger.info(f"Subscriber stats: {stats}")
        
        # Stop event manager
        logger.info("Stopping event manager...")
        event_manager.stop()
        
        logger.info("Test completed successfully.")
        return 0
        
    except Exception as e:
        logger.error(f"Error in event manager test: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main()) 