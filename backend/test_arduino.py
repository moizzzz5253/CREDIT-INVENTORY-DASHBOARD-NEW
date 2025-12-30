#!/usr/bin/env python3
"""
Standalone script to test Arduino connection and display connection status.
Run this script to check if Arduino is detected and connected.
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
backend_dir = Path(__file__).parent
app_dir = backend_dir / "app"
sys.path.insert(0, str(app_dir))

from app.services.arduino_service import arduino_service
import time

def print_separator():
    print("=" * 60)

def test_arduino_connection():
    """Test Arduino connection and display status."""
    print_separator()
    print("Arduino Connection Test")
    print_separator()
    print()
    
    # Check if serial library is available
    try:
        import serial
        import serial.tools.list_ports
        print("✓ Serial library (pyserial) is installed")
        
        # List all available ports
        print("\nAvailable Serial Ports:")
        ports = list(serial.tools.list_ports.comports())
        if ports:
            for port in ports:
                print(f"  - {port.device}: {port.description} ({port.manufacturer or 'Unknown'})")
        else:
            print("  No serial ports found!")
        print()
    except ImportError:
        print("✗ Serial library (pyserial) is NOT installed")
        print("  Install it with: pip install pyserial")
        print()
        return
    
    # Check if COM5 is in the list
    com5_found = any(p.device.upper() == 'COM5' for p in ports)
    if com5_found:
        print("✓ COM5 found in available ports!")
        print("  You can manually set it if auto-detection fails.")
        print()
    
    # Force detection
    print("Step 1: Detecting Arduino...")
    print("  (Make sure Arduino IDE Serial Monitor is CLOSED)")
    print()
    arduino_service._ensure_detected()
    print(f"  - Detection attempted: {arduino_service._detection_attempted}")
    print(f"  - Arduino port: {arduino_service.arduino_port or 'Not found'}")
    print(f"  - Connection status: {'CONNECTED' if arduino_service.is_connected else 'NOT CONNECTED'}")
    print()
    
    # If not connected but COM5 exists, offer to set it manually
    if not arduino_service.is_connected and com5_found:
        print("Step 1.5: Attempting manual connection to COM5...")
        result = arduino_service.set_port_manually('COM5')
        if result:
            print("  ✓ Successfully connected to COM5!")
            print(f"  - Connection status: {'CONNECTED' if arduino_service.is_connected else 'NOT CONNECTED'}")
        else:
            print("  ✗ Failed to connect to COM5")
            print("  - Make sure Arduino IDE Serial Monitor is CLOSED")
            print("  - Try unplugging and replugging the Arduino")
        print()
    
    if arduino_service.is_connected:
        print("✓ Arduino is CONNECTED!")
        print(f"  Port: {arduino_service.arduino_port}")
        print()
        
        # Test sending commands
        print("Step 2: Testing buzzer commands...")
        print("  - Testing SUCCESS command...")
        result = arduino_service.trigger_success_buzzer()
        if result:
            print("  ✓ SUCCESS command sent (you should hear 2 buzzer pulses)")
        else:
            print("  ✗ Failed to send SUCCESS command")
        
        time.sleep(2)  # Wait between tests
        
        print("  - Testing FAILURE command...")
        result = arduino_service.trigger_failure_buzzer()
        if result:
            print("  ✓ FAILURE command sent (you should hear 3 short buzzer pulses)")
        else:
            print("  ✗ Failed to send FAILURE command")
    else:
        print("✗ Arduino is NOT CONNECTED")
        print()
        print("Troubleshooting steps:")
        print("  1. Check if Arduino is plugged into USB port")
        print("  2. Verify Arduino drivers are installed")
        print("  3. Check Device Manager (Windows) for COM port")
        print("  4. Make sure no other program is using the serial port")
        print("  5. Try unplugging and replugging the Arduino")
        print("  6. Verify pyserial is installed: pip install pyserial")
    
    print()
    print_separator()
    
    # Keep connection info visible
    print("\nConnection Status:")
    print(f"  Connected: {arduino_service.is_connected}")
    print(f"  Port: {arduino_service.arduino_port or 'N/A'}")
    print(f"  Detection attempted: {arduino_service._detection_attempted}")
    print_separator()

if __name__ == "__main__":
    try:
        test_arduino_connection()
        
        # Keep window open
        print("\nPress Enter to exit...")
        input()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError during test: {e}")
        import traceback
        traceback.print_exc()
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)

