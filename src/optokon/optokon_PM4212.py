"""
Optokon PM-4212 (Optical Power Meter) Python Interface

This module provides a Python interface for controlling Optokon PM-4212 optical power meters
via serial connection. It supports reading power measurements from up to 4 channels.

Author: Converted from original implementation
"""

import serial
import time
import logging
from typing import List, Optional, Tuple

# Configure logging
logger = logging.getLogger(__name__)


class OptokonPM4212:
    """
    Python interface for Optokon PM-4212 Optical Power Meter.

    This class provides methods to connect to, configure, and acquire power
    measurements from an Optokon PM-4212 device via serial connection.

    Attributes:
        port (str): Serial port name (e.g. 'COM10', '/dev/ttyUSB0')
        baudrate (int): Serial communication baudrate (default: 19200)
        timeout (float): Serial read timeout in seconds
        device (serial.Serial): Serial port connection object
    """

    # Optokon PM-4212 standard parameters
    STANDARD_BAUDRATE = 19200
    STANDARD_TIMEOUT = 1.0
    WRITE_TIMEOUT = 1.0
    COMMAND_DELAY = 0.05  # Delay between command and read
    NUM_CHANNELS = 4

    def __init__(self, port: str, baudrate: int = STANDARD_BAUDRATE,
                 timeout: float = STANDARD_TIMEOUT):
        """
        Initialise Optokon PM-4212 connection parameters.

        Args:
            port: Serial port name (e.g. 'COM10' on Windows, '/dev/ttyUSB0' on Linux)
            baudrate: Serial communication speed. Default is 19200 (Optokon standard)
            timeout: Read timeout in seconds

        Raises:
            ConnectionError: If serial port cannot be opened
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.device: Optional[serial.Serial] = None
        self._connected = False

        logger.debug(f"Initialising OptokonPM4212 on {port} at {baudrate} baud")

    def connect(self) -> bool:
        """
        Establish serial connection to the Optokon PM-4212 device.

        Returns:
            bool: True if connection successful, False otherwise

        Raises:
            ConnectionError: If port cannot be opened
        """
        try:
            self.device = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=self.WRITE_TIMEOUT
            )
            # Set hardware flow control
            self.device.dtr = True
            self.device.rts = True

            self._connected = True
            logger.info(f"Connected to PM-4212 on {self.port} at {self.baudrate} baud")
            return True

        except serial.SerialException as e:
            self._connected = False
            logger.error(f"Failed to connect to {self.port}: {e}")
            raise ConnectionError(f"Cannot open serial port {self.port}: {e}")

    def disconnect(self):
        """Close the serial connection to the device."""
        if self.device and self.device.is_open:
            try:
                self.device.close()
                self._connected = False
                logger.info(f"Disconnected from PM-4212 on {self.port}")
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")

    def is_connected(self) -> bool:
        """
        Check if device is currently connected.

        Returns:
            bool: True if connected and port is open
        """
        return self._connected and self.device and self.device.is_open

    def _send_command(self, command: bytes) -> bool:
        """
        Send a command to the device.

        Args:
            command: Command bytes to send

        Returns:
            bool: True if send successful
        """
        if not self.is_connected():
            logger.error("Device not connected")
            return False

        try:
            self.device.write(command)
            logger.debug(f"Sent command: {command}")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to send command: {e}")
            return False

    def _read_response(self) -> Optional[str]:
        """
        Read response from the device.

        Args:
            timeout: Read timeout in seconds

        Returns:
            str: Response string, or None if read failed
        """
        if not self.is_connected():
            logger.error("Device not connected")
            return None

        try:
            time.sleep(self.COMMAND_DELAY)
            if self.device.in_waiting > 0:
                response = self.device.read(self.device.in_waiting).decode("ascii").strip()
                logger.debug(f"Received response: {response}")
                return response
            return None
        except Exception as e:
            logger.error(f"Failed to read response: {e}")
            return None

    def read_power(self) -> List[float]:
        """
        Read optical power from all channels.

        The PM-4212 returns up to 4 power values (one per port) in dBm.
        If a port has no fibre connected, it returns approximately -80 dBm (noise floor).

        Returns:
            List[float]: Power values in dBm for each channel. Returns empty list on error.

        Example:
            >>> meter = OptokonPM4212('COM10')
            >>> meter.connect()
            >>> powers = meter.read_power()
            >>> print(f"Channel 1: {powers[0]:.2f} dBm")
        """
        self.device.reset_input_buffer()

        # 'v' is Optokon standard command for "Value"
        if not self._send_command(b"v\r"):
            return []

        response = self._read_response()
        if not response:
            logger.warning("No response to power read command")
            return []

        # Parse response - handle multiple values
        try:
            values = []
            for value_str in response.split():
                try:
                    value = float(value_str)
                    values.append(value)
                except ValueError:
                    logger.warning(f"Could not parse value: {value_str}, using noise floor")
                    values.append(-80.0)  # Noise floor for unparseable values
            return values
        except Exception as e:
            logger.error(f"Error parsing power response: {e}")
            return []

    def read_single_channel(self, channel: int = 1) -> Optional[float]:
        """
        Read power from a single channel.

        Args:
            channel: Channel number (1-4, default: 1)

        Returns:
            float: Power in dBm, or None if read fails

        Raises:
            ValueError: If channel number is out of range
        """
        if not 1 <= channel <= self.NUM_CHANNELS:
            raise ValueError(f"Channel must be 1-{self.NUM_CHANNELS}, got {channel}")

        powers = self.read_power()
        if not powers:
            return None

        if channel <= len(powers):
            return powers[channel - 1]

        logger.warning(f"Channel {channel} not available in response")
        return None

    def get_device_info(self) -> Optional[str]:
        """
        Query device information (type and serial number).

        The 'n' command returns manufacturer-provided device information.

        Returns:
            str: Device information string, or None if query fails

        Example:
            >>> meter = OptokonPM4212('COM10')
            >>> meter.connect()
            >>> info = meter.get_device_info()
            >>> print(f"Device: {info}")
        """
        self.device.reset_input_buffer()

        # 'n' returns Type and Serial Number (Optokon standard)
        if not self._send_command(b"n\r"):
            return None

        response = self._read_response()
        if response:
            logger.info(f"Device info: {response}")
        else:
            logger.warning("Failed to retrieve device info")
        return response

    def set_wavelength(self, wavelength_nm: float) -> bool:
        """
        Set the working wavelength for power measurement.

        Different wavelengths may affect calibration. Check device manual
        for supported wavelengths (typically 850, 1310, 1550 nm).

        Args:
            wavelength_nm: Wavelength in nanometres

        Returns:
            bool: True if command sent successfully

        Note:
            Not all PM-4212 units support this command. Check your device manual.
        """
        try:
            command = f"w{wavelength_nm}\r".encode("ascii")
            success = self._send_command(command)
            if success:
                logger.info(f"Set wavelength to {wavelength_nm} nm")
            return success
        except Exception as e:
            logger.error(f"Failed to set wavelength: {e}")
            return False

    def continuous_read(self, duration_seconds: float = 10.0,
                       interval_seconds: float = 0.5) -> List[Tuple[float, List[float]]]:
        """
        Perform continuous power readings over a specified duration.

        Useful for monitoring power variations over time.

        Args:
            duration_seconds: How long to read for (seconds)
            interval_seconds: Interval between reads (seconds)

        Returns:
            List of tuples: (timestamp, [power_values]) for each reading

        Example:
            >>> meter = OptokonPM4212('COM10')
            >>> meter.connect()
            >>> readings = meter.continuous_read(duration_seconds=5.0)
            >>> for t, powers in readings:
            ...     print(f"t={t:.2f}s: Ch1={powers[0]:.2f} dBm")
        """
        readings = []
        start_time = time.time()

        logger.info(f"Starting continuous read for {duration_seconds} seconds")

        try:
            while time.time() - start_time < duration_seconds:
                elapsed = time.time() - start_time
                powers = self.read_power()
                if powers:
                    readings.append((elapsed, powers))
                    logger.debug(f"t={elapsed:.2f}s: {powers}")
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("Continuous read interrupted by user")
        except Exception as e:
            logger.error(f"Error during continuous read: {e}")

        logger.info(f"Completed {len(readings)} readings")
        return readings

    def __enter__(self):
        """Context manager entry - establish connection."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.disconnect()

    def __del__(self):
        """Destructor - ensure connection is closed."""
        self.disconnect()


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Example 1: Using context manager (recommended)
    with OptokonPM4212(port="COM10") as meter:
        info = meter.get_device_info()
        powers = meter.read_power()
        logger.info(f"Power readings: {powers}")

    # Example 2: Manual connection management
    meter = OptokonPM4212(port="COM10")
    if meter.connect():
        try:
            for i in range(5):
                powers = meter.read_power()
                logger.info(f"Reading {i+1}: {powers}")
                time.sleep(1)
        finally:
            meter.disconnect()
