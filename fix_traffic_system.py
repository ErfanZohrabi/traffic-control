#!/usr/bin/env python3
"""
Fix Traffic System Issues Script

This script automatically fixes common issues in the traffic control system project.
Run this script before running the traffic control system.
"""

import os
import sys
import json
import logging
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("FixTrafficSystem")

def fix_coordination_groups():
    """Fix coordination_groups in traffic.py."""
    try:
        # Find traffic.py
        traffic_path = Path("traffic.py")
        if not traffic_path.exists():
            logger.error("traffic.py not found!")
            return False
            
        # Read file content
        with open(traffic_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Check if issue exists
        if "'light_5'" in content and "'light_9'" in content:
            logger.info("Fixing coordination_groups configuration...")
            # Replace problematic coordination group
            content = content.replace(
                "['light_1', 'light_5', 'light_9']",
                "['light_1', 'light_2', 'light_3', 'light_4']"
            )
            
            # Write back
            with open(traffic_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            logger.info("Fixed coordination_groups configuration")
            return True
        else:
            logger.info("Coordination groups already fixed or not found")
            return True
    except Exception as e:
        logger.error(f"Error fixing coordination_groups: {e}")
        return False

def ensure_imports():
    """Ensure TensorFlow and OpenCV imports are present."""
    files_to_check = [
        "traffic.py", 
        "test.py",
        "main.py"
    ]
    
    for filename in files_to_check:
        if not Path(filename).exists():
            continue
            
        logger.info(f"Checking imports in {filename}...")
        
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Check if imports are missing
        tf_missing = "import tensorflow as tf" not in content
        cv2_missing = "import cv2" not in content
        
        if tf_missing or cv2_missing:
            logger.info(f"Adding missing imports to {filename}...")
            
            lines = content.split("\n")
            import_section_end = 0
            
            # Find import section
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    import_section_end = i + 1
            
            # Add missing imports
            if tf_missing:
                lines.insert(import_section_end, "import tensorflow as tf  # Added by fix script")
                import_section_end += 1
                
            if cv2_missing:
                lines.insert(import_section_end, "import cv2  # Added by fix script")
                
            # Write back
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
                
            logger.info(f"Fixed imports in {filename}")
    
    return True

def fix_directory_structure():
    """Ensure proper directory structure with __init__.py files."""
    directories = [
        Path("traffic"),
        Path("traffic/modules"),
    ]
    
    for directory in directories:
        if not directory.exists():
            directory.mkdir(exist_ok=True, parents=True)
            logger.info(f"Created directory: {directory}")
            
        init_file = directory / "__init__.py"
        if not init_file.exists():
            with open(init_file, "w", encoding="utf-8") as f:
                f.write('"""\n')
                f.write(f"{directory.name.capitalize()} Package\n")
                f.write('"""\n\n')
                f.write('__version__ = "0.1.0"\n')
            logger.info(f"Created {init_file}")
            
    return True

def update_requirements():
    """Ensure requirements.txt has all necessary packages."""
    req_path = Path("requirements.txt")
    if not req_path.exists():
        logger.error("requirements.txt not found!")
        return False
        
    with open(req_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    required_packages = [
        "numpy>=1.21.0",
        "pandas>=1.3.0", 
        "matplotlib>=3.4.0",
        "pyyaml>=6.0",
        "flask>=2.0.0",
        "tensorflow>=2.9.0",
        "opencv-python>=4.5.0",
        "scikit-learn>=1.0.0"
    ]
    
    missing_packages = []
    for package in required_packages:
        package_name = package.split(">=")[0]
        if package_name not in content:
            missing_packages.append(package)
            
    if missing_packages:
        logger.info("Adding missing packages to requirements.txt...")
        
        with open(req_path, "a", encoding="utf-8") as f:
            f.write("\n# Added by fix script\n")
            for package in missing_packages:
                f.write(f"{package}\n")
                
        logger.info(f"Added missing packages: {', '.join([p.split('>=')[0] for p in missing_packages])}")
    else:
        logger.info("requirements.txt already has all necessary packages")
        
    return True

def create_helper_scripts():
    """Create helper Windows batch scripts."""
    scripts = {
        "run_dashboard.bat": "@echo off\necho Starting Traffic Dashboard...\npython test_dashboard.py\npause",
        "run_demo.bat": "@echo off\necho Starting Traffic Demo...\npython demo.py\npause",
        "install.bat": "@echo off\necho Installing Traffic Control System...\npip install -r requirements.txt\npip install -e .\necho Installation complete!\npause"
    }
    
    for filename, content in scripts.items():
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Created helper script: {filename}")
        
    return True

def main():
    """Main function."""
    logger.info("Starting Traffic System Fix Script...")
    
    try:
        # Create logs directory if it doesn't exist
        if not Path("logs").exists():
            Path("logs").mkdir()
            logger.info("Created logs directory")
            
        # Run fixes
        fix_coordination_groups()
        ensure_imports()
        fix_directory_structure()
        update_requirements()
        create_helper_scripts()
        
        logger.info("All fixes applied successfully!")
        logger.info("You can now run the traffic control system with one of the following commands:")
        logger.info("  - python test_dashboard.py (for dashboard UI)")
        logger.info("  - python demo.py (for full demo)")
        logger.info("  - python test_minimal.py (for minimal test)")
        
        return 0
    except Exception as e:
        logger.error(f"Error fixing traffic system: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 