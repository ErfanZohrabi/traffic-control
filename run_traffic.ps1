# PowerShell script to install and run the Traffic Control System

# Navigate to the traffic directory if needed
# cd "C:\Path\To\Your\traffic"

# Step 1: Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Green
pip install -r requirements.txt

# Step 2: Install the package in development mode
Write-Host "Installing package in development mode..." -ForegroundColor Green
pip install -e .

# Step 3: Run the simple demo (doesn't require TensorFlow or OpenCV)
Write-Host "Starting simple traffic demo..." -ForegroundColor Green
python simple_demo.py

# Uncomment to run other options:
# python test_dashboard.py  # For dashboard UI (requires TensorFlow and OpenCV)
# python demo.py            # For full demo (requires TensorFlow and OpenCV)
# python test_minimal.py    # For minimal test
# python test_api.py        # For API test 