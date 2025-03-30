"""
Test script to verify that modules are correctly importable.
"""

try:
    print("Importing modules...")
    from modules.integration.system_integrator import SystemIntegrator, SystemConfig
    from modules.integration.event_manager import EventManager, EventPriority
    print("Successfully imported integration modules")
    
    from modules.event_logger.event_logger_controller import EventLoggerController
    print("Successfully imported event_logger module")
    
    print("All imports successful!")
except Exception as e:
    print(f"Error importing modules: {e}")
    import traceback
    traceback.print_exc() 