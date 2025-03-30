import cv2
import numpy as np
import time
import threading
import socket
import json
import queue
import logging
from collections import deque
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import argparse
import sys
import os
import tensorflow as tf
from flask import Flask, render_template, request, redirect, url_for
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("traffic_system.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("TrafficControlSystem")

#################################################
# 1. Vehicle Detection Module
#################################################

class VehicleDetector:
    """Uses basic image processing for vehicle detection and counting."""
    
    def __init__(self, confidence_threshold=0.5):
        """Initialize the vehicle detector."""
        logger.info("Initializing vehicle detector...")
        self.confidence_threshold = confidence_threshold
        
        # For counting vehicles in regions of interest
        self.tracking_history = {}
        self.vehicle_count = 0
        self.last_count_reset = time.time()
        
    def detect_vehicles(self, frame):
        """
        Detect vehicles in a frame using basic image processing.
        Returns: List of bounding boxes and vehicle types
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold
        _, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process contours
        boxes = []
        scores = []
        classes = []
        
        for contour in contours:
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by size (assuming vehicles are larger than noise)
            if w > 30 and h > 30:
                # Calculate confidence based on contour area
                area = cv2.contourArea(contour)
                confidence = min(1.0, area / (frame.shape[0] * frame.shape[1] * 0.01))
                
                if confidence > self.confidence_threshold:
                    boxes.append([x, y, x + w, y + h])
                    scores.append(confidence)
                    classes.append(2)  # Assume all are cars for testing
        
        return boxes, scores, classes
    
    def count_vehicles(self, frame, roi=None):
        """
        Count vehicles in a region of interest.
        
        Args:
            frame: The video frame
            roi: Region of interest as (x1,y1,x2,y2) or None for entire frame
            
        Returns:
            count: Number of vehicles detected
            annotated_frame: Frame with detection visualization
        """
        height, width = frame.shape[:2]
        
        if roi is None:
            roi = [0, 0, width, height]
            
        # Get detections
        boxes, scores, classes = self.detect_vehicles(frame)
        
        # Filter detections by ROI
        roi_vehicles = 0
        annotated_frame = frame.copy()
        
        for i, (box, score, class_id) in enumerate(zip(boxes, scores, classes)):
            x1, y1, x2, y2 = box
            
            # Check if the center of the box is in ROI
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            if (roi[0] <= center_x <= roi[2] and roi[1] <= center_y <= roi[3]):
                roi_vehicles += 1
                
                # Draw bounding box
                color = (0, 255, 0)  # Green for vehicles
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                
                # Display confidence
                label = f"Vehicle: {score:.2f}"
                cv2.putText(annotated_frame, label, (x1, y1-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw ROI
        cv2.rectangle(annotated_frame, (roi[0], roi[1]), (roi[2], roi[3]), (255, 0, 0), 2)
        
        # Display vehicle count
        cv2.putText(annotated_frame, f"Vehicles: {roi_vehicles}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        return roi_vehicles, annotated_frame


#################################################
# 2. Traffic Density Calculator
#################################################

class TrafficDensityCalculator:
    """Calculate traffic density based on vehicle counts."""
    
    def __init__(self, window_size=10, congestion_threshold=15):
        """
        Initialize traffic density calculator.
        
        Args:
            window_size: Number of frames to consider for moving average
            congestion_threshold: Threshold for congestion determination
        """
        self.window_size = window_size
        self.congestion_threshold = congestion_threshold
        self.vehicle_counts = deque(maxlen=window_size)
        self.density_history = deque(maxlen=100)
        self.last_update_time = time.time()
        
    def update(self, vehicle_count):
        """Update with new vehicle count."""
        self.vehicle_counts.append(vehicle_count)
        
        # Record timestamp of update
        current_time = time.time()
        time_diff = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Calculate current density
        density = self.calculate_density()
        self.density_history.append(density)
        
        return density
        
    def calculate_density(self):
        """Calculate current traffic density."""
        if not self.vehicle_counts:
            return 0
        
        avg_count = sum(self.vehicle_counts) / len(self.vehicle_counts)
        
        # Normalize density between 0 and 1
        density = min(1.0, avg_count / self.congestion_threshold)
        
        return density
    
    def get_congestion_level(self):
        """
        Get congestion level based on current density.
        Returns one of: 'low', 'medium', 'high'
        """
        density = self.calculate_density()
        
        if density < 0.3:
            return 'low'
        elif density < 0.7:
            return 'medium'
        else:
            return 'high'
    
    def get_density_trend(self):
        """Calculate if traffic density is increasing, decreasing or stable."""
        if len(self.density_history) < 2:
            return 'stable'
            
        # Get recent density values
        recent = list(self.density_history)[-5:]
        
        if len(recent) < 5:
            return 'stable'
            
        # Calculate slope of trend
        x = list(range(len(recent)))
        y = recent
        
        # Simple linear regression to find slope
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x_i * y_i for x_i, y_i in zip(x, y))
        sum_xx = sum(x_i * x_i for x_i in x)
        
        # Calculate slope
        try:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
            
            if slope > 0.05:
                return 'increasing'
            elif slope < -0.05:
                return 'decreasing'
            else:
                return 'stable'
        except ZeroDivisionError:
            return 'stable'


#################################################
# 3. Traffic Light Controller
#################################################

class TrafficLight:
    """Represents a single traffic light."""
    
    def __init__(self, id, initial_timing=None):
        """
        Initialize a traffic light.
        
        Args:
            id: Unique identifier for this traffic light
            initial_timing: Dictionary with initial timing in seconds for each phase
        """
        self.id = id
        
        # Default timings if none provided
        if initial_timing is None:
            initial_timing = {
                'green': 30,
                'yellow': 5,
                'red': 30
            }
            
        self.timing = initial_timing
        self.current_phase = 'red'
        self.phase_start_time = time.time()
        self.connected_lights = []  # IDs of connected traffic lights
        
        # Store history of timing adjustments
        self.timing_history = []
        
        logger.info(f"Traffic light {id} initialized with timing: {initial_timing}")
    
    def get_current_phase(self):
        """Get current phase of the traffic light."""
        current_time = time.time()
        elapsed = current_time - self.phase_start_time
        
        # Check if we need to transition to the next phase
        if elapsed >= self.timing[self.current_phase]:
            self.transition_to_next_phase()
            
        return self.current_phase
    
    def transition_to_next_phase(self):
        """Transition to the next traffic light phase."""
        # Define phase transition order
        if self.current_phase == 'green':
            next_phase = 'yellow'
        elif self.current_phase == 'yellow':
            next_phase = 'red'
        else:  # red
            next_phase = 'green'
            
        self.current_phase = next_phase
        self.phase_start_time = time.time()
        
        logger.debug(f"Traffic light {self.id} transitioned to {next_phase} phase")
        
        return next_phase
    
    def adjust_timing(self, phase, new_time):
        """
        Adjust timing for a specific phase.
        
        Args:
            phase: The phase to adjust ('green', 'yellow', 'red')
            new_time: New duration in seconds
        """
        if phase not in self.timing:
            logger.error(f"Invalid phase: {phase}")
            return False
            
        # Don't allow yellow to be too short (safety)
        if phase == 'yellow' and new_time < 3:
            new_time = 3
            
        # Record the adjustment
        self.timing_history.append({
            'timestamp': time.time(),
            'phase': phase,
            'old_value': self.timing[phase],
            'new_value': new_time
        })
        
        # Update the timing
        self.timing[phase] = new_time
        logger.info(f"Traffic light {self.id} adjusted {phase} phase to {new_time}s")
        
        return True
    
    def get_time_remaining(self):
        """Get remaining time in the current phase."""
        current_time = time.time()
        elapsed = current_time - self.phase_start_time
        remaining = max(0, self.timing[self.current_phase] - elapsed)
        
        return remaining
    
    def force_phase(self, new_phase):
        """Force traffic light to a specific phase."""
        if new_phase not in ['red', 'yellow', 'green']:
            logger.error(f"Invalid phase: {new_phase}")
            return False
            
        self.current_phase = new_phase
        self.phase_start_time = time.time()
        
        logger.info(f"Traffic light {self.id} forced to {new_phase} phase")
        return True


class TrafficLightController:
    """Controls a network of traffic lights."""
    
    def __init__(self):
        """Initialize the traffic light controller."""
        self.traffic_lights = {}  # id -> TrafficLight
        self.traffic_densities = {}  # id -> density value
        self.coordination_groups = []  # Groups of coordinated lights
        
    def add_traffic_light(self, id, initial_timing=None):
        """Add a new traffic light to the network."""
        if id in self.traffic_lights:
            logger.warning(f"Traffic light {id} already exists")
            return self.traffic_lights[id]
            
        light = TrafficLight(id, initial_timing)
        self.traffic_lights[id] = light
        self.traffic_densities[id] = 0.0
        
        return light
    
    def update_traffic_density(self, light_id, density):
        """Update traffic density for a specific traffic light."""
        if light_id not in self.traffic_lights:
            logger.error(f"Unknown traffic light: {light_id}")
            return False
            
        self.traffic_densities[light_id] = density
        logger.debug(f"Updated density for light {light_id}: {density:.2f}")
        
        # Adjust timing based on new density
        self._adjust_timing_based_on_density(light_id, density)
        
        return True
    
    def _adjust_timing_based_on_density(self, light_id, density):
        """Adjust timing based on current traffic density."""
        light = self.traffic_lights[light_id]
        
        # Basic adjustment algorithm (can be more sophisticated)
        base_green_time = 30  # seconds
        max_green_time = 60   # seconds
        min_green_time = 15   # seconds
        
        # Adjust green time based on density
        new_green_time = int(base_green_time + (max_green_time - base_green_time) * density)
        new_green_time = max(min_green_time, min(max_green_time, new_green_time))
        
        # Adjust red time inversely
        red_time = max(min_green_time, int(base_green_time * (1 - density * 0.5)))
        
        # Keep yellow time constant for safety
        yellow_time = light.timing['yellow']
        
        # Apply adjustments
        light.adjust_timing('green', new_green_time)
        light.adjust_timing('red', red_time)
        
        logger.debug(f"Adjusted light {light_id} timing: green={new_green_time}s, red={red_time}s")
    
    def create_coordination_group(self, light_ids):
        """Create a group of coordinated traffic lights."""
        # Validate all light IDs
        for light_id in light_ids:
            if light_id not in self.traffic_lights:
                logger.error(f"Cannot create coordination group: Unknown traffic light: {light_id}")
                return False
        
        self.coordination_groups.append(light_ids)
        logger.info(f"Created coordination group: {light_ids}")
        
        # Connect the lights to each other
        for light_id in light_ids:
            light = self.traffic_lights[light_id]
            light.connected_lights = [id for id in light_ids if id != light_id]
            
        return True
    
    def coordinate_lights(self):
        """
        Coordinate traffic lights in all groups.
        This implements a simplified green wave approach.
        """
        for group in self.coordination_groups:
            self._coordinate_group(group)
    
    def _coordinate_group(self, light_ids):
        """Coordinate a group of traffic lights to create a green wave."""
        if not light_ids or len(light_ids) < 2:
            return
            
        # Find the light with highest traffic density
        max_density = -1
        max_density_light = None
        
        for light_id in light_ids:
            density = self.traffic_densities.get(light_id, 0)
            if density > max_density:
                max_density = density
                max_density_light = light_id
        
        if not max_density_light:
            return
            
        # Prioritize the highest density light
        prioritized_light = self.traffic_lights[max_density_light]
        
        # If prioritized light is not green and has high density, make it green
        if prioritized_light.current_phase != 'green' and max_density > 0.7:
            # Force other lights in the group to coordinate
            self._force_green_wave(light_ids, max_density_light)
    
    def _force_green_wave(self, light_ids, starting_light_id):
        """
        Force a green wave starting from the specified light.
        This is a simplified implementation of green wave coordination.
        """
        # Average distance between traffic lights (in meters)
        avg_distance = 300
        
        # Average vehicle speed (in meters/second)
        avg_speed = 14  # ~50 km/h or ~30 mph
        
        # Calculate time offset for green wave (time to travel from one light to the next)
        time_offset = avg_distance / avg_speed
        
        starting_light = self.traffic_lights[starting_light_id]
        
        # Force the starting light to green
        if starting_light.current_phase != 'green':
            # If it's red and about to turn green anyway, don't force it
            if starting_light.current_phase == 'red' and starting_light.get_time_remaining() < 5:
                pass
            else:
                # If it's yellow, let it finish yellow before turning green
                if starting_light.current_phase == 'yellow':
                    # Wait for yellow to complete
                    pass
                else:
                    starting_light.force_phase('green')
        
        # Order lights by their position in the corridor (simplified)
        # In a real implementation, you would have actual positions
        ordered_lights = light_ids.copy()
        
        # Set offsets for subsequent lights
        current_offset = time_offset
        
        for i in range(1, len(ordered_lights)):
            light_id = ordered_lights[i]
            light = self.traffic_lights[light_id]
            
            # Schedule this light to turn green after the offset
            # In a real implementation, you would use a scheduling mechanism
            # For now, we'll just calculate when it should turn green
            target_green_time = time.time() + current_offset
            
            # Calculate current cycle position
            current_time = time.time()
            cycle_position = (light.current_phase, light.get_time_remaining())
            
            logger.debug(f"Light {light_id} cycle position: {cycle_position}")
            
            # In a real implementation, you would adjust the timing to hit the target
            # For this example, we'll just log the target time
            logger.info(f"Light {light_id} should turn green at offset: {current_offset:.1f}s")
            
            # Increment offset for next light
            current_offset += time_offset


#################################################
# 4. Inter-Traffic Light Communication
#################################################

class CommunicationManager:
    """Manages communication between traffic lights and control center."""
    
    def __init__(self, host='127.0.0.1', port=5555):
        """Initialize communication manager."""
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_connections = {}  # id -> socket
        self.message_queue = queue.Queue()
        self.running = False
        
    def start_server(self):
        """Start the communication server."""
        if self.running:
            logger.warning("Communication server already running")
            return
            
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            
            self.running = True
            
            # Start server thread
            server_thread = threading.Thread(target=self._accept_connections)
            server_thread.daemon = True
            server_thread.start()
            
            # Start message processing thread
            message_thread = threading.Thread(target=self._process_messages)
            message_thread.daemon = True
            message_thread.start()
            
            logger.info(f"Communication server started on {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Failed to start communication server: {e}")
            self.running = False
            raise
    
    def _accept_connections(self):
        """Accept incoming client connections."""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                logger.info(f"New connection from {address}")
                
                # Start a thread to handle this client
                client_thread = threading.Thread(
                    target=self._handle_client, 
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    logger.error(f"Error accepting connection: {e}")
    
    def _handle_client(self, client_socket, address):
        """Handle communication with a connected client."""
        client_id = None
        
        try:
            # First message should contain client ID
            data = client_socket.recv(1024)
            if not data:
                logger.warning(f"Client {address} disconnected before sending ID")
                return
                
            # Parse the registration message
            try:
                message = json.loads(data.decode('utf-8'))
                if 'id' in message:
                    client_id = message['id']
                    self.client_connections[client_id] = client_socket
                    logger.info(f"Registered client {client_id} from {address}")
                else:
                    logger.warning(f"Client did not provide ID: {message}")
                    return
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from client: {data}")
                return
            
            # Main client handling loop
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    logger.info(f"Client {client_id} disconnected")
                    break
                    
                try:
                    message = json.loads(data.decode('utf-8'))
                    message['sender'] = client_id
                    self.message_queue.put(message)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from client {client_id}: {data}")
        
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        
        finally:
            # Clean up
            if client_id and client_id in self.client_connections:
                del self.client_connections[client_id]
            
            try:
                client_socket.close()
            except:
                pass
    
    def _process_messages(self):
        """Process messages from the queue."""
        while self.running:
            try:
                message = self.message_queue.get(timeout=1.0)
                
                # Process based on message type
                if 'type' in message:
                    if message['type'] == 'status_update':
                        self._handle_status_update(message)
                    elif message['type'] == 'command':
                        self._handle_command(message)
                    else:
                        logger.warning(f"Unknown message type: {message['type']}")
                
                self.message_queue.task_done()
                
            except queue.Empty:
                # Queue timeout, just continue
                pass
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    def _handle_status_update(self, message):
        """Handle status update messages from traffic lights."""
        # In a real system, you would update a database or state management system
        logger.debug(f"Status update from {message['sender']}: {message}")
    
    def _handle_command(self, message):
        """Handle command messages."""
        if 'target' in message:
            target = message['target']
            
            if target in self.client_connections:
                try:
                    self.client_connections[target].sendall(
                        json.dumps(message).encode('utf-8')
                    )
                    logger.debug(f"Sent command to {target}")
                except Exception as e:
                    logger.error(f"Failed to send command to {target}: {e}")
            else:
                logger.warning(f"Target {target} not connected")
    
    def send_message(self, target_id, message_type, data):
        """
        Send a message to a specific traffic light.
        
        Args:
            target_id: ID of the target traffic light
            message_type: Type of message ('command', 'config', etc.)
            data: Message data (dictionary)
        """
        if not self.running:
            logger.error("Communication server not running")
            return False
            
        if target_id not in self.client_connections:
            logger.warning(f"Target {target_id} not connected")
            return False
            
        message = {
            'type': message_type,
            'target': target_id,
            'data': data,
            'timestamp': time.time()
        }
        
        try:
            self.client_connections[target_id].sendall(
                json.dumps(message).encode('utf-8')
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {target_id}: {e}")
            return False
    
    def broadcast_message(self, message_type, data):
        """Broadcast a message to all connected traffic lights."""
        if not self.running:
            logger.error("Communication server not running")
            return
            
        message = {
            'type': message_type,
            'data': data,
            'timestamp': time.time()
        }
        
        encoded_message = json.dumps(message).encode('utf-8')
        
        for client_id, client_socket in list(self.client_connections.items()):
            try:
                client_socket.sendall(encoded_message)
            except Exception as e:
                logger.error(f"Failed to broadcast to {client_id}: {e}")
    
    def stop(self):
        """Stop the communication server."""
        self.running = False
        
        # Close all client connections
        for client_id, client_socket in list(self.client_connections.items()):
            try:
                client_socket.close()
            except:
                pass
        
        self.client_connections.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            
        logger.info("Communication server stopped")


#################################################
# 5. System Integration
#################################################

class TrafficControlSystem:
    """Main class integrating all components of the traffic control system."""
    
    def __init__(self, config_file=None):
        """Initialize the traffic control system."""
        logger.info("Initializing Traffic Control System")
        
        # Load configuration
        self.config = self._load_config(config_file)
        
        # Initialize components
        self.vehicle_detectors = {}  # camera_id -> VehicleDetector
        self.density_calculators = {}  # intersection_id -> TrafficDensityCalculator
        self.traffic_controller = TrafficLightController()
        
        # Initialize communication
        host = self.config.get('communication', {}).get('host', '127.0.0.1')
        port = self.config.get('communication', {}).get('port', 5555)
        self.communication = CommunicationManager(host, port)
        
        # Performance metrics
        self.metrics = {
            'detection_fps': [],
            'response_times': [],
            'congestion_levels': {}
        }
        
        # System state
        self.running = False
        self.last_metrics_update = time.time()
    
    def _load_config(self, config_file):
        """Load system configuration from file."""
        default_config = {
            'system': {
                'log_level': 'INFO',
                'metrics_interval': 300  # seconds
            },
            'detection': {
                'confidence_threshold': 0.5,
                'model_path': 'yolov5s.pt'
            },
            'traffic': {
                'congestion_threshold': 15,
                'window_size': 10
            },
            'communication': {
                'host': '127.0.0.1',
                'port': 5555
            },
            'intersections': [
                {
                    'id': 'intersection_1',
                    'cameras': ['camera_1', 'camera_2'],
                    'traffic_lights': ['light_1', 'light_2', 'light_3', 'light_4'],
                    'initial_timing': {
                        'green': 30,
                        'yellow': 5,
                        'red': 30
                    }
                }
            ],
            'coordination_groups': [
                ['light_1', 'light_2', 'light_3', 'light_4']  # Updated to use only existing traffic lights
            ]
        }
        
        if config_file:
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    # Deep merge user config with default config
                    self.config = self._deep_merge(default_config, user_config)
            except Exception as e:
                logger.error(f"Failed to load config file: {e}")
                self.config = default_config
        else:
            self.config = default_config
            
        return self.config
    
    def _deep_merge(self, dict1, dict2):
        """Deep merge two dictionaries."""
        result = dict1.copy()
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def start(self):
        """Start the traffic control system."""
        if self.running:
            logger.warning("Traffic control system already running")
            return
            
        try:
            # Start communication server
            self.communication.start_server()
            
            # Initialize vehicle detectors for each camera
            for intersection in self.config['intersections']:
                for camera_id in intersection['cameras']:
                    self.vehicle_detectors[camera_id] = VehicleDetector(
                        confidence_threshold=self.config['detection']['confidence_threshold']
                    )
                    
                # Initialize density calculator for each intersection
                self.density_calculators[intersection['id']] = TrafficDensityCalculator(
                    window_size=self.config['traffic']['window_size'],
                    congestion_threshold=self.config['traffic']['congestion_threshold']
                )
                
                # Initialize traffic lights
                for light_id in intersection['traffic_lights']:
                    self.traffic_controller.add_traffic_light(
                        light_id,
                        initial_timing=intersection['initial_timing']
                    )
            
            # Create coordination groups
            for group in self.config['coordination_groups']:
                self.traffic_controller.create_coordination_group(group)
            
            self.running = True
            
            # Start main processing loop
            self._main_loop()
            
        except Exception as e:
            logger.error(f"Failed to start traffic control system: {e}")
            self.stop()
            raise
    
    def _main_loop(self):
        """Main processing loop of the system."""
        while self.running:
            try:
                # Process each intersection
                for intersection in self.config['intersections']:
                    intersection_id = intersection['id']
                    density_calc = self.density_calculators[intersection_id]
                    
                    # Process each camera
                    total_vehicles = 0
                    for camera_id in intersection['cameras']:
                        # In a real system, you would get the frame from the camera
                        # For now, we'll simulate with a blank frame
                        frame = np.zeros((640, 640, 3), dtype=np.uint8)
                        
                        # Detect vehicles
                        vehicle_count, annotated_frame = self.vehicle_detectors[camera_id].count_vehicles(frame)
                        total_vehicles += vehicle_count
                        
                        # Update density calculator
                        density = density_calc.update(total_vehicles)
                        
                        # Update traffic controller
                        for light_id in intersection['traffic_lights']:
                            self.traffic_controller.update_traffic_density(light_id, density)
                    
                    # Coordinate traffic lights
                    self.traffic_controller.coordinate_lights()
                    
                    # Update metrics
                    self._update_metrics(intersection_id, density)
                
                # Sleep to maintain desired processing rate
                time.sleep(0.1)  # 10 FPS
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(1)  # Wait before retrying
    
    def _update_metrics(self, intersection_id, density):
        """Update system metrics."""
        current_time = time.time()
        
        # Update congestion levels
        self.metrics['congestion_levels'][intersection_id] = {
            'density': density,
            'level': self.density_calculators[intersection_id].get_congestion_level(),
            'trend': self.density_calculators[intersection_id].get_density_trend(),
            'timestamp': current_time
        }
        
        # Update metrics periodically
        if current_time - self.last_metrics_update >= self.config['system']['metrics_interval']:
            self._save_metrics()
            self.last_metrics_update = current_time
    
    def _save_metrics(self):
        """Save system metrics to file."""
        try:
            metrics_file = f"traffic_metrics_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
            logger.info(f"Metrics saved to {metrics_file}")
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def stop(self):
        """Stop the traffic control system."""
        self.running = False
        
        # Stop communication server
        self.communication.stop()
        
        # Save final metrics
        self._save_metrics()
        
        logger.info("Traffic control system stopped")


if __name__ == "__main__":
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description='Traffic Control System')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                      default='DEBUG', help='Set the logging level')
    parser.add_argument('--model-path', type=str, default='yolov5s.pt',
                      help='Path to YOLOv5 model file')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                      help='Host address for communication server')
    parser.add_argument('--port', type=int, default=5555,
                      help='Port for communication server')
    args = parser.parse_args()
    
    # Update logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    try:
        logger.debug("Starting system initialization...")
        logger.debug(f"Current working directory: {os.getcwd()}")
        logger.debug(f"Python version: {sys.version}")
        logger.debug(f"TensorFlow version: {tf.__version__}")
        logger.debug(f"OpenCV version: {cv2.__version__}")
        
        # Create and start the traffic control system
        system = TrafficControlSystem(config_file=args.config)
        
        # Override config with command line arguments
        if args.model_path:
            system.config['detection']['model_path'] = args.model_path
        if args.host:
            system.config['communication']['host'] = args.host
        if args.port:
            system.config['communication']['port'] = args.port
            
        logger.info("Starting Traffic Control System...")
        logger.info(f"Configuration: {json.dumps(system.config, indent=2)}")
        
        system.start()
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        system.stop()
    except Exception as e:
        logger.error(f"System error: {e}", exc_info=True)
        if 'system' in locals():
            system.stop()
        sys.exit(1)

app = Flask(__name__)

# Example statistics data (in a real application, this would be dynamic)
statistics_data = {
    'total_vehicles': 0,
    'average_density': 0,
    'traffic_light_changes': 0,
    'peak_hour': None,
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/traffic-status')
def traffic_status():
    # Example traffic status data
    traffic_status = {
        'light_1': {'current_phase': 'green', 'density_level': 'medium'},
        'light_2': {'current_phase': 'red', 'density_level': 'high'},
    }
    return render_template('traffic_status.html', traffic_status=traffic_status)

@app.route('/control', methods=['GET', 'POST'])
def control():
    if request.method == 'POST':
        light_id = request.form['light_id']
        phase = request.form['phase']
        # Here you would call the method to set the traffic light phase
        # For example: traffic_controller.force_phase(light_id, phase)
        statistics_data['traffic_light_changes'] += 1  # Increment light change count
        return redirect(url_for('control'))
    return render_template('control.html')

@app.route('/statistics')
def statistics():
    # Calculate average density and peak hour (dummy values for example)
    statistics_data['total_vehicles'] += 10  # Simulate vehicle detection
    statistics_data['average_density'] = statistics_data['total_vehicles'] / 10  # Example calculation
    current_hour = datetime.datetime.now().hour
    statistics_data['peak_hour'] = current_hour if current_hour > 8 and current_hour < 10 else "N/A"  # Example logic

    return render_template('statistics.html', 
                           total_vehicles=statistics_data['total_vehicles'],
                           average_density=statistics_data['average_density'],
                           traffic_light_changes=statistics_data['traffic_light_changes'],
                           peak_hour=statistics_data['peak_hour'])

@app.route('/dashboard')
def dashboard():
    # Simulated data for the dashboard
    labels = [f"Hour {i}" for i in range(24)]  # Simulate hourly data for a day
    vehicle_counts = [random.randint(0, 100) for _ in range(24)]  # Random vehicle counts for each hour

    return render_template('dashboard.html', labels=labels, vehicle_counts=vehicle_counts)

if __name__ == '__main__':
    app.run(debug=True)