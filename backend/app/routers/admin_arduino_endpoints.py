"""
Arduino status endpoints for admin router.
These endpoints are imported and added to the admin router.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.services.arduino_service import arduino_service

class PortRequest(BaseModel):
    port: str

# These will be added to the admin router
def add_arduino_routes(router):
    """Add Arduino-related routes to the admin router."""
    
    @router.get("/arduino/status")
    def get_arduino_status():
        """
        Get Arduino connection status.
        Returns information about whether Arduino is detected and connected.
        """
        try:
            # Force detection if not already attempted
            if not arduino_service._detection_attempted:
                arduino_service._ensure_detected()
            
            # Get list of available ports for debugging
            available_ports = arduino_service.list_available_ports()
            
            return {
                "connected": arduino_service.is_connected,
                "port": arduino_service.arduino_port,
                "detection_attempted": arduino_service._detection_attempted,
                "serial_available": True,
                "available_ports": available_ports
            }
        except Exception as e:
            return {
                "connected": False,
                "port": None,
                "detection_attempted": False,
                "error": str(e),
                "available_ports": []
            }
    
    @router.post("/arduino/test-success")
    def test_arduino_success():
        """
        Test Arduino success buzzer (2 pulses with 1 second delay).
        """
        try:
            result = arduino_service.trigger_success_buzzer()
            return {
                "success": result,
                "message": "Success buzzer triggered (2 pulses)" if result else "Failed to trigger buzzer - Arduino not connected"
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error testing buzzer: {str(e)}"
            )
    
    @router.post("/arduino/test-failure")
    def test_arduino_failure():
        """
        Test Arduino failure buzzer (3 short pulses with 0.5 second delay).
        """
        try:
            result = arduino_service.trigger_failure_buzzer()
            return {
                "success": result,
                "message": "Failure buzzer triggered (3 short pulses)" if result else "Failed to trigger buzzer - Arduino not connected"
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error testing buzzer: {str(e)}"
            )
    
    @router.post("/arduino/set-port")
    def set_arduino_port(port_request: PortRequest):
        """
        Manually set Arduino port (e.g., 'COM5').
        Useful when auto-detection fails but you know the port from Arduino IDE.
        Body: {"port": "COM5"}
        """
        try:
            port = port_request.port.strip().upper()  # Normalize to uppercase
            if not port:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Port parameter is required (e.g., {'port': 'COM5'})"
                )
            
            result = arduino_service.set_port_manually(port)
            if result:
                return {
                    "success": True,
                    "connected": arduino_service.is_connected,
                    "port": arduino_service.arduino_port,
                    "message": f"Arduino port set to {port} and connected successfully"
                }
            else:
                return {
                    "success": False,
                    "connected": False,
                    "port": None,
                    "message": f"Failed to connect to {port}. Make sure Arduino IDE Serial Monitor is closed."
                }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error setting port: {str(e)}"
            )
        """
        Manually set Arduino port (e.g., 'COM5').
        Useful when auto-detection fails but you know the port from Arduino IDE.
        """
        try:
            result = arduino_service.set_port_manually(port)
            if result:
                return {
                    "success": True,
                    "connected": arduino_service.is_connected,
                    "port": arduino_service.arduino_port,
                    "message": f"Arduino port set to {port} and connected successfully"
                }
            else:
                return {
                    "success": False,
                    "connected": False,
                    "port": None,
                    "message": f"Failed to connect to {port}. Make sure Arduino IDE Serial Monitor is closed."
                }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error setting port: {str(e)}"
            )
    
    @router.post("/arduino/redetect")
    def redetect_arduino():
        """
        Force re-detection of Arduino.
        Useful if Arduino was plugged in after server startup.
        """
        try:
            # Reset detection state
            arduino_service._detection_attempted = False
            arduino_service.is_connected = False
            arduino_service.arduino_port = None
            
            # Close existing connection if any
            if arduino_service.serial_connection:
                try:
                    arduino_service.serial_connection.close()
                except:
                    pass
                arduino_service.serial_connection = None
            
            # Force new detection
            arduino_service._ensure_detected()
            
            return {
                "success": True,
                "connected": arduino_service.is_connected,
                "port": arduino_service.arduino_port,
                "message": f"Arduino {'detected' if arduino_service.is_connected else 'not detected'}"
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error re-detecting Arduino: {str(e)}"
            )

