# Traffic Control System Quick Start Guide

This guide will help you quickly set up and run the Traffic Control System with minimal configuration.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation in 3 Steps

### 1. Clone and Setup

```bash
# Install dependencies
pip install numpy pandas matplotlib pyyaml requests flask

# Navigate to the traffic directory
cd traffic
```

### 2. Install the Package

```bash
# Install in development mode
pip install -e .
```

### 3. Check Installation

```bash
# Verify installation with a simple import test
python test_import.py
```

You should see a success message if everything is installed correctly.

## Running the System

### Option 1: Run the Dashboard Demo (Recommended for First-Time Users)

The dashboard demo provides a visual web interface to monitor the traffic system:

```bash
python test_dashboard.py
```

This will:
- Start the traffic control system
- Launch a web dashboard at http://localhost:8080
- Simulate traffic for 60 seconds
- Display traffic lights and events in real-time

### Option 2: Run the Full Simulation Demo

For a more comprehensive demo with various traffic scenarios:

```bash
python demo.py
```

This will:
- Initialize the complete traffic control system
- Simulate multiple traffic lights
- Generate various events (emergency vehicles, weather, etc.)
- Run for 200 time steps (approximately 2 minutes)

### Option 3: Run a Minimal Test

For a quick test of core functionality:

```bash
python test_minimal.py
```

This runs just the essential components to verify system operation.

## Common Tasks

### Viewing Logs

Logs are stored in the `logs/` directory, with the most recent run appearing in:
```
logs/traffic_system_YYYYMMDD_HHMMSS.log
```

### Testing Event Communication

To specifically test the event manager system:

```bash
python test_event_manager.py
```

### Running with Custom Configuration

Create a custom YAML configuration file:

```yaml
# config.yaml
system:
  log_level: DEBUG
  update_interval: 0.5

modules:
  dashboard:
    enabled: true
    port: 8080
```

Then run with:

```bash
python main.py --config config.yaml
```

## Next Steps

1. **Explore the Dashboard**: Open http://localhost:8080 while running the dashboard test
2. **Review the Logs**: Check the generated logs to understand system behavior
3. **Experiment with Parameters**: Try different simulation parameters in demo.py
4. **Read the Documentation**: See README_UPDATED.md for comprehensive documentation

## Troubleshooting

### "ModuleNotFoundError"
- Ensure you're in the correct directory
- Verify that you ran `pip install -e .`

### "Address already in use" when starting dashboard
- Another process is using port 8080
- Modify the dashboard port in the configuration or close the other application

### System exits immediately
- Check the logs for error messages
- Try running with debug logging: `python main.py --log-level DEBUG`

## Quick Reference

| Command | Description |
|---------|-------------|
| `python test_dashboard.py` | Run with visual dashboard |
| `python demo.py` | Run full simulation demo |
| `python test_minimal.py` | Run minimal system test |
| `python main.py --simulation` | Run main system in simulation mode |
| `python main.py --dashboard-only` | Run only the dashboard server |
| `python main.py --log-level DEBUG` | Run with detailed logging | 