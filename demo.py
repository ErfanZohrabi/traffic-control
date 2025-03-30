"""
Demo script for the Traffic Control System.
"""

import logging
import time
import json
import os
import random
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("TrafficDemo")

def setup_directories():
    """Create necessary directories for logs and data storage."""
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/reports", exist_ok=True)
    
def simulate_traffic_data(light_id, time_step):
    """Generate simulated traffic data for a traffic light."""
    # Simulate daily traffic pattern (busier in morning and evening)
    hour = (time_step % 24)
    base_density = 0.2
    
    # Morning rush (7-9 AM)
    if 7 <= hour < 9:
        base_density = 0.7
    # Evening rush (4-7 PM)
    elif 16 <= hour < 19:
        base_density = 0.8
    # Night time (11 PM - 5 AM)
    elif hour < 5 or hour >= 23:
        base_density = 0.1
        
    # Add some randomness
    density = base_density + random.uniform(-0.1, 0.1)
    density = max(0.05, min(0.95, density))  # Keep between 0.05 and 0.95
    
    # Occasionally simulate congestion
    if random.random() < 0.05:
        density += 0.2
        density = min(0.95, density)
    
    return {
        "density": density,
        "vehicle_count": int(density * 100),
        "average_speed": max(5, 60 * (1 - density)),
        "timestamp": datetime.now().isoformat()
    }

def simulate_events(system, time_step):
    """Simulate various events in the traffic system."""
    # 5% chance of generating a special event each time step
    if random.random() < 0.05:
        event_types = [
            "emergency",
            "public_transport",
            "pedestrian",
            "weather",
        ]
        event_type = random.choice(event_types)
        
        if event_type == "emergency":
            # Simulate emergency vehicle
            event_data = {
                "type": "vehicle_approaching",
                "vehicle_id": f"emergency_{random.randint(1000, 9999)}",
                "location": {
                    "lat": 40.712776 + random.uniform(-0.01, 0.01),
                    "lng": -74.005974 + random.uniform(-0.01, 0.01)
                },
                "speed": 60 + random.uniform(0, 20),
                "heading": random.uniform(0, 360)
            }
            logger.info(f"Emergency vehicle approaching: {event_data['vehicle_id']}")
            
        elif event_type == "public_transport":
            # Simulate public transport vehicle
            event_data = {
                "type": "vehicle_approaching",
                "vehicle_id": f"bus_{random.randint(1000, 9999)}",
                "location": {
                    "lat": 40.712776 + random.uniform(-0.01, 0.01),
                    "lng": -74.005974 + random.uniform(-0.01, 0.01)
                },
                "route": f"Route-{random.randint(1, 10)}",
                "schedule_status": {
                    "on_time": random.choice([True, False]),
                    "delay": random.uniform(0, 10) if random.random() < 0.3 else 0
                }
            }
            logger.info(f"Public transport approaching: {event_data['vehicle_id']} on {event_data['route']}")
            
        elif event_type == "pedestrian":
            # Simulate pedestrian crossing request
            event_data = {
                "type": "button_press",
                "crossing_id": f"crossing_{random.randint(1, 20)}",
                "count": random.randint(1, 5)
            }
            logger.info(f"Pedestrian crossing request at {event_data['crossing_id']}")
            
        elif event_type == "weather":
            # Simulate weather update
            weather_types = ["rain", "snow", "fog", "clear", "windy"]
            severity_levels = ["light", "moderate", "severe", "extreme"]
            
            weather_type = random.choice(weather_types)
            # Higher chance of extreme weather for snow and rain
            severity_weights = [0.5, 0.3, 0.15, 0.05]
            if weather_type in ["snow", "rain"]:
                severity_weights = [0.3, 0.3, 0.3, 0.1]
                
            severity = random.choices(severity_levels, weights=severity_weights)[0]
            
            event_data = {
                "weather_type": weather_type,
                "severity": severity,
                "location": {
                    "lat": 40.712776,
                    "lng": -74.005974
                },
                "prediction": {
                    "duration": random.randint(1, 12),  # hours
                    "intensity_trend": random.choice(["increasing", "stable", "decreasing"])
                }
            }
            logger.info(f"Weather update: {severity} {weather_type}")
        
        # Publish the event
        system.add_event(
            event_type=event_type,
            data=event_data
        )
        
def run_demo():
    """Run the traffic control system demo."""
    try:
        logger.info("Setting up demo environment...")
        setup_directories()
        
        logger.info("Importing required modules...")
        from modules.integration.system_integrator import SystemIntegrator, SystemConfig
        from modules.event_logger.event_logger_controller import EventLoggerConfig
        
        logger.info("Creating system configuration...")
        system_config = SystemConfig(
            update_interval=0.5,
            max_concurrent_tasks=4,
            log_level="INFO",
            event_manager_workers=2,
            health_check_interval=30,
            event_logger_config=EventLoggerConfig(
                database_path="data/events.db",
                retention_days=7,
                report_path="data/reports"
            )
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
            "intersection_side_2",
        ]
        
        for light_id in traffic_lights:
            initial_state = {
                "id": light_id,
                "phase": "red",
                "density": 0.2,
                "vehicle_count": 0,
                "active": True
            }
            system.register_traffic_light(light_id, initial_state)
            logger.info(f"Registered traffic light: {light_id}")
        
        # Run simulation for a period of time
        logger.info("Starting traffic simulation...")
        logger.info("Press Ctrl+C to stop the demo.")
        
        try:
            for time_step in range(200):  # Run for 200 time steps
                # Update traffic data for each traffic light
                for light_id in traffic_lights:
                    traffic_data = simulate_traffic_data(light_id, time_step)
                    
                    # Update traffic light
                    system.update_traffic_light(light_id, {
                        "density": traffic_data["density"],
                        "vehicle_count": traffic_data["vehicle_count"]
                    })
                    
                    # Also publish as event
                    system.add_event(
                        event_type="traffic_update",
                        data={
                            "light_id": light_id,
                            "density": traffic_data["density"],
                            "vehicle_count": traffic_data["vehicle_count"],
                            "average_speed": traffic_data["average_speed"]
                        }
                    )
                
                # Simulate random events
                simulate_events(system, time_step)
                
                # Print status every 10 steps
                if time_step % 10 == 0:
                    logger.info(f"Simulation time step: {time_step}/200")
                    
                    # Get state of a random traffic light
                    random_light = random.choice(traffic_lights)
                    light_state = system.get_traffic_light_state(random_light)
                    logger.info(f"Traffic light {random_light} state: {light_state}")
                    
                    # Get system status
                    system_status = system.get_system_status()
                    logger.info(f"Active modules: {system_status['active_modules']}")
                    logger.info(f"Traffic light count: {system_status['traffic_light_count']}")
                    logger.info(f"Event queue size: {system_status['event_queue_size']}")
                
                time.sleep(0.2)  # Speed up the simulation
        
        except KeyboardInterrupt:
            logger.info("Demo interrupted by user.")
        
        # Generate a report from the event logger
        try:
            event_logger = system.modules.get('event_logger')
            if event_logger:
                logger.info("Generating traffic report...")
                
                end_time = datetime.now().isoformat()
                start_time = (datetime.now() - timedelta(hours=1)).isoformat()
                
                report_path = event_logger.generate_report(
                    report_type="overview",
                    start_time=start_time,
                    end_time=end_time
                )
                
                if report_path:
                    logger.info(f"Report generated: {report_path}")
                    
                    # Generate charts
                    for chart_type in ["event_frequency", "event_types", "event_sources"]:
                        chart_path = event_logger.generate_chart(
                            chart_type=chart_type,
                            start_time=start_time,
                            end_time=end_time
                        )
                        if chart_path:
                            logger.info(f"Chart generated: {chart_path}")
        except Exception as e:
            logger.error(f"Error generating report: {e}")
        
        logger.info("Stopping system...")
        system.stop()
        
        logger.info("Demo completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Error in demo: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(run_demo()) 