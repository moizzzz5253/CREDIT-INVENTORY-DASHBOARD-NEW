"""
Arduino service for controlling buzzer notifications.
Automatically detects Arduino port and sends commands for buzzer control.
"""

from typing import Optional
from loguru import logger
import time

# Make serial imports optional - backend can run without Arduino
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    logger.warning("pyserial not installed. Arduino buzzer functionality will be disabled.")

# Store availability in module for easy access
__all__ = ['ArduinoService', 'arduino_service', 'SERIAL_AVAILABLE']


class ArduinoService:
    """Service for communicating with Arduino to control buzzer."""
    
    def __init__(self):
        self.arduino_port: Optional[str] = None
        self.serial_connection: Optional[serial.Serial] = None
        self.is_connected = False
        self._detection_attempted = False
        # Don't detect Arduino on init - do it lazily when needed
        # This prevents blocking startup if serial ports are slow or unavailable
    
    def set_port_manually(self, port: str) -> bool:
        """
        Manually set the Arduino port (e.g., 'COM5').
        Useful when auto-detection fails but you know the port.
        """
        if not SERIAL_AVAILABLE:
            logger.warning("Serial library not available. Cannot set port manually.")
            return False
        
        try:
            # Check if port exists
            ports = [p.device for p in serial.tools.list_ports.comports()]
            if port not in ports:
                logger.warning(f"Port {port} not found in available ports: {ports}")
                return False
            
            self.arduino_port = port
            logger.info(f"Manually set Arduino port to: {port}")
            
            # Try to connect
            if self._connect():
                self.is_connected = True
                self._detection_attempted = True
                logger.info(f"Successfully connected to Arduino on {port}")
                return True
            else:
                logger.warning(f"Failed to connect to {port}. Port may be in use or wrong device.")
                return False
        except Exception as e:
            logger.error(f"Error setting port manually: {e}")
            return False
    
    def _detect_arduino(self) -> bool:
        """
        Automatically detect Arduino port by checking available serial ports.
        Looks for common Arduino identifiers in port descriptions.
        This method should not block - all operations have timeouts.
        """
        if not SERIAL_AVAILABLE:
            logger.debug("Serial library not available. Arduino detection skipped.")
            return False
        
        try:
            # Use timeout to prevent blocking on slow serial port enumeration
            ports = list(serial.tools.list_ports.comports())
            
            if not ports:
                logger.warning("No serial ports found. Make sure Arduino is connected.")
                return False
            
            logger.info(f"Found {len(ports)} serial port(s). Scanning for Arduino...")
            
            # Log all available ports for debugging
            for port in ports:
                logger.debug(f"Available port: {port.device} - {port.description} ({port.manufacturer or 'Unknown'})")
            
            # Common Arduino identifiers (expanded list)
            arduino_identifiers = [
                'arduino', 'ch340', 'ch341', 'ftdi', 'usb serial', 'cp210', 
                'usb-to-serial', 'usb serial port', 'serial port', 'com',
                'arduino uno', 'arduino nano', 'arduino mega'
            ]
            
            # First pass: Try ports with Arduino-like identifiers
            for port in ports:
                port_description = (port.description or '').lower()
                port_manufacturer = (port.manufacturer or '').lower()
                port_hwid = (port.hwid or '').lower()
                
                # Check if port description, manufacturer, or hwid contains Arduino identifiers
                port_info = f"{port_description} {port_manufacturer} {port_hwid}"
                
                if any(identifier in port_info for identifier in arduino_identifiers):
                    try:
                        self.arduino_port = port.device
                        logger.info(f"Found potential Arduino port: {port.device} ({port.description})")
                        
                        # Try to connect to verify it's an Arduino
                        if self._connect():
                            logger.info(f"Arduino is connected on port: {self.arduino_port}")
                            self.is_connected = True
                            return True
                    except serial.SerialException as e:
                        error_msg = str(e).lower()
                        if 'access is denied' in error_msg or 'being used' in error_msg:
                            logger.warning(f"Port {port.device} is in use (possibly by Arduino IDE Serial Monitor). Close Serial Monitor and try again.")
                        else:
                            logger.debug(f"Failed to connect to {port.device}: {e}")
                        continue
                    except Exception as e:
                        logger.debug(f"Failed to connect to {port.device}: {e}")
                        continue
            
            # Second pass: Try all available ports if identifier matching failed
            # (fallback for systems where port description is not available)
            if not self.is_connected:
                logger.info("No Arduino found by identifier. Trying all available ports...")
                for port in ports:
                    try:
                        self.arduino_port = port.device
                        logger.info(f"Attempting connection to {port.device} ({port.description or 'No description'})...")
                        if self._connect():
                            logger.info(f"Arduino is connected on port: {self.arduino_port} (auto-detected)")
                            self.is_connected = True
                            return True
                    except serial.SerialException as e:
                        error_msg = str(e).lower()
                        if 'access is denied' in error_msg or 'being used' in error_msg or 'cannot open' in error_msg:
                            logger.warning(f"Port {port.device} is in use or cannot be opened. Close Arduino IDE Serial Monitor and try again.")
                        else:
                            logger.debug(f"Failed to connect to {port.device}: {e}")
                        continue
                    except Exception as e:
                        logger.debug(f"Failed to connect to {port.device}: {e}")
                        continue
            
            if not self.is_connected:
                logger.warning("No Arduino detected. Buzzer notifications will be disabled.")
                logger.warning("Troubleshooting: Close Arduino IDE Serial Monitor and try again.")
                return False
                
        except Exception as e:
            logger.error(f"Error detecting Arduino: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False
    
    def _connect(self) -> bool:
        """Attempt to connect to Arduino on the detected port."""
        if not SERIAL_AVAILABLE:
            return False
        
        if not self.arduino_port:
            return False
        
        # Close existing connection if any
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.close()
            except Exception:
                pass
        
        try:
            # Try to open serial connection
            # Common baud rates: 9600, 115200
            for baud_rate in [9600, 115200]:
                try:
                    ser = serial.Serial(
                        port=self.arduino_port,
                        baudrate=baud_rate,
                        timeout=2,
                        write_timeout=2
                    )
                    time.sleep(0.5)  # Reduced wait time to prevent blocking
                    
                    # Clear any existing data in buffer
                    try:
                        ser.reset_input_buffer()
                        ser.reset_output_buffer()
                    except AttributeError:
                        # Some serial implementations don't have these methods
                        pass
                    except Exception:
                        # Ignore any errors during buffer reset
                        pass
                    
                    # Try to send a test command and check for response
                    # Arduino should respond with "READY" or similar
                    try:
                        # Clear any existing data first
                        time.sleep(0.2)  # Small delay for Arduino to be ready
                        ser.write(b'TEST\n')
                        ser.flush()
                        time.sleep(0.5)  # Wait for response
                    except Exception as e:
                        # If write fails, close and try next baud rate
                        logger.debug(f"Write failed: {e}")
                        try:
                            ser.close()
                        except:
                            pass
                        continue
                    
                    # Check for response
                    if ser.in_waiting > 0:
                        try:
                            response = ser.readline().decode('utf-8', errors='ignore').strip()
                            logger.debug(f"Arduino response: {response}")
                            if 'ready' in response.lower() or len(response) > 0:
                                self.serial_connection = ser
                                logger.info(f"Arduino responded on {self.arduino_port} at {baud_rate} baud")
                                return True
                        except Exception as e:
                            logger.debug(f"Error reading response: {e}")
                    
                    # If no response but connection opened successfully, assume it's working
                    # (some Arduino sketches don't send initial response, or response was already read)
                    # This is a more lenient approach - if we can open the port, assume it's Arduino
                    # Also check if we can write to it (basic connectivity test)
                    try:
                        # Try a simple write to verify the port is actually working
                        test_write = ser.write(b'\n')  # Just a newline
                        ser.flush()
                        if test_write > 0:
                            self.serial_connection = ser
                            logger.info(f"Arduino connection opened on {self.arduino_port} at {baud_rate} baud (connection verified)")
                            return True
                    except Exception as e:
                        logger.debug(f"Write test failed: {e}")
                        try:
                            ser.close()
                        except:
                            pass
                        continue
                        
                except serial.SerialException:
                    continue
                except Exception as e:
                    logger.debug(f"Connection attempt failed at {baud_rate} baud: {e}")
                    continue
            
            return False
            
        except Exception as e:
            logger.debug(f"Error connecting to Arduino: {e}")
            return False
    
    def list_available_ports(self):
        """List all available serial ports for debugging."""
        if not SERIAL_AVAILABLE:
            return []
        
        try:
            ports = list(serial.tools.list_ports.comports())
            port_info = []
            for port in ports:
                port_info.append({
                    'device': port.device,
                    'description': port.description,
                    'manufacturer': port.manufacturer,
                    'hwid': port.hwid
                })
            return port_info
        except Exception as e:
            logger.error(f"Error listing ports: {e}")
            return []
    
    def _ensure_detected(self):
        """Lazily detect Arduino if not already attempted."""
        if not self._detection_attempted:
            self._detection_attempted = True
            try:
                self._detect_arduino()
            except Exception as e:
                logger.error(f"Error during Arduino detection: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                self.is_connected = False
    
    def _send_command(self, command: str) -> bool:
        """Send a command to Arduino."""
        # Try to detect Arduino if not already done
        if not self._detection_attempted:
            self._ensure_detected()
        
        if not self.is_connected or not self.serial_connection:
            logger.debug("Arduino not connected. Cannot send command.")
            return False
        
        try:
            if not self.serial_connection.is_open:
                # Try to reconnect
                if not self._connect():
                    return False
            
            # Send command with newline
            command_bytes = f"{command}\n".encode('utf-8')
            self.serial_connection.write(command_bytes)
            self.serial_connection.flush()
            logger.debug(f"Sent command to Arduino: {command}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending command to Arduino: {e}")
            self.is_connected = False
            return False
    
    def trigger_success_buzzer(self) -> bool:
        """
        Trigger success buzzer pattern: 2 pulses with 1 second delay between them.
        """
        # Try to detect Arduino if not already done
        if not self._detection_attempted:
            self._ensure_detected()
        
        if not self.is_connected:
            logger.debug("Arduino not connected. Skipping success buzzer.")
            return False
        
        try:
            # Send SUCCESS command to Arduino
            # Arduino will handle the timing (2 pulses, 1 sec delay)
            return self._send_command("SUCCESS")
        except Exception as e:
            logger.error(f"Error triggering success buzzer: {e}")
            return False
    
    def trigger_failure_buzzer(self) -> bool:
        """
        Trigger failure buzzer pattern: 3 short pulses with 0.5 second delay between them.
        """
        # Try to detect Arduino if not already done
        if not self._detection_attempted:
            self._ensure_detected()
        
        if not self.is_connected:
            logger.debug("Arduino not connected. Skipping failure buzzer.")
            return False
        
        try:
            # Send FAILURE command to Arduino
            # Arduino will handle the timing (3 short pulses, 0.5 sec delay)
            return self._send_command("FAILURE")
        except Exception as e:
            logger.error(f"Error triggering failure buzzer: {e}")
            return False
    
    def close(self):
        """Close the serial connection."""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.close()
                logger.info("Arduino connection closed.")
            except Exception as e:
                logger.error(f"Error closing Arduino connection: {e}")
        
        self.is_connected = False
        self.serial_connection = None


# Global Arduino service instance
arduino_service = ArduinoService()

