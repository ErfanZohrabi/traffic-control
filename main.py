#!/usr/bin/env python3
import argparse
import logging
import os
import sys
import time
import json
import yaml
from datetime import datetime
import threading
import signal
import importlib
from typing import Dict, Any, List, Optional

# Import modules
from modules.integration.config_manager import ConfigManager
from modules.integration.system_integrator import SystemIntegrator, SystemConfig
from modules.integration.event_manager import EventManager, EventPriority
from modules.green_wave.green_wave_controller import GreenWaveController, GreenWaveConfig
from modules.emergency.emergency_controller import EmergencyController, EmergencyConfig
from modules.public_transport.public_transport_controller import PublicTransportController, PublicTransportConfig
from modules.pedestrian.pedestrian_controller import PedestrianController, PedestrianConfig
from modules.analytics.analytics_controller import AnalyticsController, AnalyticsConfig
from modules.weather.weather_controller import WeatherController, WeatherConfig
from modules.mobile_app.mobile_app_controller import MobileAppController, MobileAppConfig
from modules.ml_prediction.prediction_controller import PredictionController, PredictionConfig
from modules.dashboard.dashboard_controller import DashboardController, DashboardConfig
from modules.simulation.simulation_controller import SimulationController, SimulationConfig
from modules.v2i.v2i_controller import V2IController, V2IConfig

def setup_logging(log_level, log_file=None):
    """Set up logging configuration."""
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    level = log_levels.get(log_level, logging.INFO)
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Default log file name if not provided
    if log_file is None:
        log_file = f'logs/traffic_system_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Create logger
    logger = logging.getLogger('TrafficControlSystem')
    logger.info(f"Logging initialized at level {log_level}")
    return logger

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Traffic Control System')
    parser.add_argument('--simulation', action='store_true', help='Run in simulation mode')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--log-level', type=str, default='INFO', 
                      choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                      help='Set the logging level')
    parser.add_argument('--log-file', type=str, help='Path to log file')
    parser.add_argument('--real-time-factor', type=float, default=1.0,
                      help='Real-time factor for simulation (>1 = faster)')
    parser.add_argument('--modules', type=str, help='Comma-separated list of modules to load')
    parser.add_argument('--dashboard-only', action='store_true', help='Run only the dashboard server')
    parser.add_argument('--export-config', type=str, help='Export default configuration to file')
    return parser.parse_args()

def load_config(config_path=None):
    """Load system configuration."""
    config_manager = ConfigManager()
    
    if config_path and os.path.exists(config_path):
        # Load from provided file
        if config_manager.load_config(config_path):
            logging.info(f"Configuration loaded from {config_path}")
            return config_manager.get_config()
    
    # If no config provided or loading failed, create default config
    logging.info("Using default configuration")
    return config_manager.create_default_config()

def export_default_config(export_path):
    """Export default configuration to a file."""
    config_manager = ConfigManager()
    default_config = config_manager.create_default_config()
    
    # Determine format from file extension
    file_ext = os.path.splitext(export_path)[1].lower()
    
    try:
        if file_ext == '.json':
            with open(export_path, 'w') as f:
                json.dump(default_config, f, indent=2, default=str)
        elif file_ext in ['.yaml', '.yml']:
            with open(export_path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
        else:
            logging.error(f"Unsupported file format: {file_ext}. Use .json, .yaml, or .yml")
            return False
            
        logging.info(f"Default configuration exported to {export_path}")
        return True
    except Exception as e:
        logging.error(f"Error exporting configuration: {e}")
        return False

def discover_modules():
    """Discover available modules in the system."""
    modules_dir = os.path.join(os.path.dirname(__file__), 'modules')
    modules = []
    
    for item in os.listdir(modules_dir):
        if os.path.isdir(os.path.join(modules_dir, item)) and not item.startswith('__'):
            # Check if this is a valid module
            controller_path = os.path.join(modules_dir, item, f"{item}_controller.py")
            if os.path.exists(controller_path):
                modules.append(item)
    
    return modules

def load_module_class(module_name):
    """Dynamically load a module controller class."""
    try:
        # Import the module
        module_path = f"modules.{module_name}.{module_name}_controller"
        module = importlib.import_module(module_path)
        
        # Find the controller class
        # Convention: ModuleNameController (e.g., GreenWaveController)
        class_name = ''.join(word.capitalize() for word in module_name.split('_')) + 'Controller'
        
        if hasattr(module, class_name):
            return getattr(module, class_name)
        else:
            logging.warning(f"Controller class {class_name} not found in {module_path}")
            return None
    
    except ImportError as e:
        logging.error(f"Error importing module {module_name}: {e}")
        return None
    except Exception as e:
        logging.error(f"Error loading module {module_name}: {e}")
        return None

def setup_signal_handlers(system):
    """Set up signal handlers for graceful shutdown."""
    def signal_handler(sig, frame):
        if sig == signal.SIGINT:
            logging.info("Received interrupt signal. Shutting down...")
        elif sig == signal.SIGTERM:
            logging.info("Received termination signal. Shutting down...")
        
        if system:
            system.stop()
        
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Main entry point for the traffic control system."""
    # Parse command-line arguments
    args = parse_args()
    
    # Handle config export request
    if args.export_config:
        if export_default_config(args.export_config):
            print(f"Default configuration exported to {args.export_config}")
            return 0
        else:
            print("Failed to export configuration")
            return 1
    
    # Setup logging
    logger = setup_logging(args.log_level, args.log_file)
    
    # Handle dashboard-only mode
    if args.dashboard_only:
        logger.info("Starting in dashboard-only mode")
        return run_dashboard()
    
    # Load configuration
    config = load_config(args.config)
    
    # Initialize controllers
    logger.info("Initializing controllers...")
    
    try:
        # Initialize the main system integrator
        system_config = SystemConfig(**config.get('system', {}))
        system = SystemIntegrator(system_config)
        
        # Set up signal handlers for graceful shutdown
        setup_signal_handlers(system)
        
        # Get list of modules to load
        modules_to_load = []
        if args.modules:
            modules_to_load = [m.strip() for m in args.modules.split(',')]
        else:
            # Auto-discover available modules
            modules_to_load = discover_modules()
            logger.info(f"Discovered modules: {', '.join(modules_to_load)}")
        
        # Load modules dynamically
        for module_name in modules_to_load:
            try:
                module_config_key = module_name.replace('-', '_')
                module_config = config.get(module_config_key, {})
                
                # Skip disabled modules
                if isinstance(module_config, dict) and not module_config.get('enabled', True):
                    logger.info(f"Module {module_name} is disabled in configuration, skipping")
                    continue
                
                # Load module class
                controller_class = load_module_class(module_name)
                if controller_class:
                    # Create instance
                    module_instance = controller_class(module_config)
                    
                    # Register with system integrator
                    system.register_module(module_name, module_instance)
                    logger.info(f"Module {module_name} loaded and registered")
            except Exception as e:
                logger.error(f"Error loading module {module_name}: {e}")
        
        # Initialize simulation if needed
        simulation = None
        if args.simulation:
            logger.info("Initializing simulation mode...")
            
            # Import and configure simulation
            from modules.simulation.simulation_controller import SimulationController
            
            sim_config = config.get('simulation', {})
            if args.real_time_factor:
                sim_config['real_time_factor'] = args.real_time_factor
                
            simulation = SimulationController(sim_config)
            system.register_module('simulation', simulation)
        
        # Start services
        logger.info("Starting services...")
        
        try:
            # Start the main system integrator
            system.start()
            
            # Start simulation if in simulation mode
            if simulation:
                simulation.start_simulation()
                
                # Set up data flow from simulation to system
                simulator_thread = threading.Thread(
                    target=simulation_data_flow,
                    args=(simulation, system),
                    daemon=True
                )
                simulator_thread.start()
            
            # Keep the main thread running
            logger.info("Traffic Control System running. Press Ctrl+C to exit.")
            
            # Enter main loop
            while True:
                # Monitor system health
                system_status = system.get_system_status()
                if system_status['running']:
                    module_health = system.get_module_health()
                    
                    # Check for unhealthy modules
                    unhealthy_modules = [
                        name for name, status in module_health.items()
                        if not status['healthy']
                    ]
                    
                    if unhealthy_modules:
                        logger.warning(f"Unhealthy modules detected: {', '.join(unhealthy_modules)}")
                        
                        # Attempt to restart unhealthy modules
                        for module_name in unhealthy_modules:
                            logger.info(f"Attempting to restart module: {module_name}")
                            system.restart_module(module_name)
                
                time.sleep(30)  # Check every 30 seconds
        
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received. Shutting down...")
        except Exception as e:
            logger.error(f"Error in main execution: {e}", exc_info=True)
        finally:
            # Stop services
            logger.info("Shutting down Traffic Control System...")
            
            if simulation:
                simulation.stop_simulation()
            
            system.stop()
            
            logger.info("System shutdown complete.")
    
    except Exception as e:
        logger.error(f"Error initializing system: {e}", exc_info=True)
        return 1
    
    return 0

def simulation_data_flow(simulation, system):
    """Data flow from simulation to system components."""
    try:
        logger = logging.getLogger("SimulationDataFlow")
        logger.info("Starting simulation data flow")
        
        # Get module references
        prediction_controller = system.modules.get('ml_prediction')
        dashboard_controller = system.modules.get('dashboard')
        
        while simulation.simulation_running and system.running:
            # Get traffic data from simulation
            traffic_data = simulation.get_traffic_data()
            
            # Update dashboard with traffic data
            if dashboard_controller:
                for light_id, data in traffic_data.items():
                    dashboard_controller.update_traffic_data(light_id, data)
            
            # Update prediction model with simulation data
            if prediction_controller:
                for light_id, data in traffic_data.items():
                    prediction_controller.add_historical_data(light_id, data)
                    
                    # Generate predictions for this light
                    current_data = data.copy()
                    predictions = prediction_controller.predict(light_id, current_data)
                    
                    # Update predictions in dashboard
                    if predictions and dashboard_controller:
                        dashboard_controller.update_prediction_data(light_id, predictions)
                    
                    # Publish prediction event to system
                    system.add_event(
                        event_type="ml_prediction",
                        data={
                            "type": "traffic_prediction",
                            "light_id": light_id,
                            "predictions": predictions or {}
                        }
                    )
            
            # Process V2I messages if available
            v2i_controller = system.modules.get('v2i')
            if v2i_controller:
                v2i_messages = simulation.get_v2i_messages() if hasattr(simulation, 'get_v2i_messages') else []
                for message in v2i_messages:
                    v2i_controller._process_message(message, ('127.0.0.1', 0))
            
            # Sleep before next update
            time.sleep(1)
    
    except Exception as e:
        logging.error(f"Error in simulation data flow: {e}", exc_info=True)

def run_dashboard():
    """Run the dashboard server separately."""
    try:
        # First, check if the dashboard module is available
        dashboard_module_path = os.path.join(
            os.path.dirname(__file__), 
            'modules', 
            'dashboard', 
            'dashboard_server.py'
        )
        
        if not os.path.exists(dashboard_module_path):
            logging.error("Dashboard module not found. Please make sure it's installed correctly.")
            return 1
        
        # Import dashboard server module
        from modules.dashboard.dashboard_server import run_dashboard_server
        
        # Run dashboard server
        logging.info("Starting dashboard server...")
        run_dashboard_server()
        
        return 0
    except ImportError as e:
        logging.error(f"Error importing dashboard server: {e}")
        return 1
    except Exception as e:
        logging.error(f"Error running dashboard: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 