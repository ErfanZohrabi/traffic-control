# Advanced Traffic Control System

## Overview
The Advanced Traffic Control System is a comprehensive solution for intelligent traffic management in urban environments. It uses a modular architecture to integrate various traffic control features, including traffic light management, emergency vehicle prioritization, public transport integration, and pedestrian safety.

The system is designed with a focus on:
- **Modular architecture**: Easy to extend with new functionality
- **Event-based communication**: Efficient inter-module data exchange
- **Real-time visualization**: Web-based dashboard for monitoring
- **Simulation capabilities**: Testing scenarios without physical hardware
- **Analytics and logging**: Comprehensive data collection for analysis

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           System Integrator                                  │
├─────────┬─────────┬────────┬──────────┬─────────┬────────────┬──────────────┤
│ Green   │Emergency│ Public │Pedestrian│ Weather │  Analytics │      ML      │
│  Wave   │ Control │Transport│ Safety  │   Data  │ & Logging  │  Prediction  │
├─────────┴─────────┴────────┴──────────┴─────────┴────────────┴──────────────┤
│                           Event Manager                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                       Traffic Light Control Network                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Components

### Core Components
- **System Integrator**: Coordinates all modules and manages system-wide operations
- **Event Manager**: Handles inter-module communication using a publish-subscribe pattern
- **Config Manager**: Manages system and module configuration

### Feature Modules
- **Green Wave Controller**: Coordinates traffic flow across multiple intersections
- **Emergency Controller**: Prioritizes emergency vehicles in traffic
- **Public Transport Controller**: Provides priority for buses and public transport
- **Pedestrian Controller**: Enhances pedestrian safety at crossings
- **Weather Controller**: Adapts traffic management based on weather conditions
- **Analytics Controller**: Collects and analyzes traffic data
- **ML Prediction Controller**: Uses machine learning to predict traffic patterns
- **Dashboard Controller**: Provides a web interface for monitoring and control
- **Mobile App Controller**: Connects with drivers via mobile applications
- **V2I Controller**: Vehicle-to-Infrastructure communication
- **Event Logger**: Records all system events for analysis

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd traffic
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Running the System

### Basic Usage

To run the complete traffic control system:
```bash
python main.py
```

### Common Command Line Options

- **Simulation Mode**: `python main.py --simulation`
- **Configure Logging**: `python main.py --log-level DEBUG`
- **Use Custom Config**: `python main.py --config myconfig.yaml`
- **Dashboard Only**: `python main.py --dashboard-only`
- **Export Default Config**: `python main.py --export-config config.yaml`

### Running Specific Tests

1. Minimal System Test:
   ```bash
   python test_minimal.py
   ```

2. Event Manager Test:
   ```bash
   python test_event_manager.py
   ```

3. Dashboard Test (with Web UI):
   ```bash
   python test_dashboard.py
   ```

4. Demo Simulation:
   ```bash
   python demo.py
   ```

## Dashboard

The system includes a web-based dashboard for real-time monitoring:
- Access at: http://localhost:8080 (when dashboard module is running)
- Features:
  - Traffic light status visualization
  - Real-time event log
  - System status indicators
  - Traffic density monitoring

## Module Structure

Each module follows a consistent structure:
```
modules/
├── module_name/
│   ├── __init__.py
│   ├── module_name_controller.py  # Main controller
│   ├── config.py                  # Module-specific configuration
│   └── utils/                     # Module-specific utilities
```

## Extending the System

### Adding a New Module

1. Create a new directory in the `modules` folder
2. Implement a controller class that extends `ModuleInterface`
3. Register your module with the System Integrator

Example:
```python
from ..integration.module_interface import ModuleInterface

class MyNewController(ModuleInterface):
    def __init__(self, config=None):
        # Initialize module
        
    def initialize(self, config):
        # Setup with configuration
        return True
        
    def start(self):
        # Start module operation
        return True
        
    def stop(self):
        # Stop module operation
        return True
        
    def process_event(self, event):
        # Handle incoming events
        return None
        
    def get_status(self):
        # Return module status
        return {"status": "running"}
```

## Configuration

The system uses a hierarchical configuration system:
1. Default configuration built into the code
2. Configuration file (JSON or YAML)
3. Command-line parameters (highest priority)

Example configuration (YAML):
```yaml
system:
  update_interval: 1.0
  log_level: INFO
  event_manager_workers: 2

modules:
  green_wave:
    enabled: true
    corridor_priority: high
    
  emergency:
    enabled: true
    preemption_distance: 500
```

## File Organization

```
traffic/
├── main.py                # Main entry point
├── demo.py                # Demonstration script
├── requirements.txt       # Python dependencies
├── setup.py               # Package installation
├── README.md              # Documentation
├── modules/               # System modules
│   ├── integration/       # Core system components
│   ├── dashboard/         # Web UI
│   ├── event_logger/      # Event logging
│   └── [other modules]/   # Feature modules
├── test_*.py              # Various test scripts
├── data/                  # Data storage
└── logs/                  # Log files
```

## Testing

The system includes several test scripts:
- `test_minimal.py`: Basic system functionality
- `test_event_manager.py`: Event system testing
- `test_dashboard.py`: Dashboard visualization
- `test_system.py`: Complete system test

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**:
   - Ensure you've installed the package in development mode with `pip install -e .`
   - Check that your PYTHONPATH includes the project root

2. **Failed to start module**:
   - Check logs for specific error messages
   - Verify module dependencies are installed
   - Check configuration settings for the module

3. **Dashboard not showing data**:
   - Ensure the system is running and generating events
   - Check the browser console for JavaScript errors
   - Verify the dashboard module is properly initialized

### Logging

Logs are stored in the `logs/` directory. For more detailed logs, run with:
```bash
python main.py --log-level DEBUG
```

## Performance Considerations

- **Event Queue Size**: Large numbers of events may impact performance
- **Database Growth**: The event logger database will grow over time; enable retention policies
- **Simulation Speed**: Adjust the real-time factor for faster/slower simulations

## Future Enhancements

Planned improvements to the system include:
- Machine learning-based traffic prediction
- Cloud-based analytics platform
- Mobile app for citizen reporting
- Multi-intersection optimization
- Integration with real traffic signal hardware

## Contributing

Contributions to the project are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please contact [erfanzohrabi.ez@gmail.com](mailto:erfanzohrabi.ez@gmail.com). 