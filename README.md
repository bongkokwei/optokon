# Optokon PM-4212 Python Interface

A Python interface for controlling Optokon PM-4212 optical power meters via serial connection. This library provides a modern, type-annotated interface with both programmatic and GUI access to power measurements.

## Overview

The Optokon PM-4212 is a compact optical power meter measuring optical power in up to 4 channels simultaneously. This Python package provides:

- **Simple serial interface** to read power measurements from 4 channels
- **Type hints** for improved IDE support
- **Logging support** for debugging and monitoring
- **PyQt5 GUI** for real-time monitoring with live plotting
- **Context manager support** for clean resource management

## Features

- Serial connection management with automatic reconnection handling
- Read power from 1 to 4 channels simultaneously
- Query device information (type, serial number)
- Support for wavelength selection (device-dependent)
- Continuous monitoring with configurable intervals
- Real-time graphical monitoring with PyQt5/pyqtgraph
- Comprehensive logging throughout
- Type hints for improved IDE support

## Installation

### Requirements

- Python 3.7+
- pyserial ≥ 3.5
- (Optional) PyQt5 ≥ 5.15.0 and pyqtgraph ≥ 0.13.0 for GUI

### Install Dependencies

```bash
pip install pyserial
```

For GUI support:

```bash
pip install PyQt5 pyqtgraph numpy
```

### Import the Class

```python
from optokon_pm4212 import OptokonPM4212
```

## Quick Start

### Basic Usage

```python
from optokon_pm4212 import OptokonPM4212
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialise connection
meter = OptokonPM4212(port='COM10')

# Connect to device
meter.connect()

# Read power from all channels
powers = meter.read_power()
print(f"Channel 1: {powers[0]:.2f} dBm")
print(f"Channel 2: {powers[1]:.2f} dBm")

# Disconnect
meter.disconnect()
```

### Using Context Manager (Recommended)

```python
from optokon_pm4212 import OptokonPM4212

with OptokonPM4212(port='COM10') as meter:
    powers = meter.read_power()
    print(f"Powers: {powers}")
    # Connection automatically closed
```

### Continuous Monitoring

```python
with OptokonPM4212(port='COM10') as meter:
    readings = meter.continuous_read(duration_seconds=10, interval_seconds=0.5)
    for timestamp, powers in readings:
        print(f"t={timestamp:.2f}s: {powers}")
```

### Running the GUI

```bash
python -m src/optokon/optokon_gui.py
```

Or programmatically:

```python
from optokon_pm4212.gui import main
main()
```

## API Reference

### Initialisation

#### `OptokonPM4212(port, baudrate, timeout)`

Initialise an Optokon PM-4212 connection object.

**Parameters:**
- `port` (str): Serial port name (e.g. `'COM10'` on Windows, `'/dev/ttyUSB0'` on Linux)
- `baudrate` (int, optional): Serial communication speed. Default: `19200` (Optokon standard)
- `timeout` (float, optional): Read timeout in seconds. Default: `1.0`

**Example:**
```python
meter = OptokonPM4212(port='COM10', timeout=1.0)
```

---

### Connection Management

#### `connect() -> bool`

Establish serial connection to the device.

**Returns:**
- `bool`: True if connection successful

**Raises:**
- `ConnectionError`: If serial port cannot be opened

**Example:**
```python
meter = OptokonPM4212(port='COM10')
if meter.connect():
    print("Connected")
```

#### `disconnect()`

Close the serial connection to the device.

**Example:**
```python
meter.disconnect()
```

#### `is_connected() -> bool`

Check if device is currently connected.

**Returns:**
- `bool`: True if connected and port is open

**Example:**
```python
if meter.is_connected():
    powers = meter.read_power()
```

---

### Measurement Methods

#### `read_power() -> List[float]`

Read optical power from all available channels.

Power values are returned in dBm (decibels relative to 1 milliwatt). If a port has no fibre connected, it typically returns approximately −80 dBm (noise floor).

**Returns:**
- `List[float]`: Power values in dBm for each channel

**Example:**
```python
powers = meter.read_power()
print(f"Channel 1: {powers[0]:.2f} dBm")
print(f"Channel 2: {powers[1]:.2f} dBm")
print(f"Channel 3: {powers[2]:.2f} dBm")
print(f"Channel 4: {powers[3]:.2f} dBm")
```

#### `read_single_channel(channel) -> Optional[float]`

Read power from a single channel.

**Parameters:**
- `channel` (int): Channel number 1–4

**Returns:**
- `float`: Power in dBm, or None if read fails

**Raises:**
- `ValueError`: If channel number is out of range

**Example:**
```python
power_ch1 = meter.read_single_channel(channel=1)
if power_ch1:
    print(f"Channel 1: {power_ch1:.2f} dBm")
```

#### `continuous_read(duration_seconds, interval_seconds) -> List[Tuple[float, List[float]]]`

Perform continuous power readings over a specified duration.

Useful for monitoring power variations over time or logging measurements.

**Parameters:**
- `duration_seconds` (float): How long to read for (seconds). Default: `10.0`
- `interval_seconds` (float): Interval between reads (seconds). Default: `0.5`

**Returns:**
- `List[Tuple[float, List[float]]]`: List of (timestamp, [power_values]) tuples

**Example:**
```python
readings = meter.continuous_read(duration_seconds=5.0, interval_seconds=0.1)
for timestamp, powers in readings:
    print(f"t={timestamp:.2f}s: {powers}")
```

---

### Device Information

#### `get_device_info() -> Optional[str]`

Query device information (type and serial number).

Returns manufacturer-provided device identification.

**Returns:**
- `str`: Device information string, or None if query fails

**Example:**
```python
info = meter.get_device_info()
print(f"Device: {info}")
```

#### `set_wavelength(wavelength_nm) -> bool`

Set the working wavelength for power measurement.

Different wavelengths may affect calibration. Check your device manual for supported wavelengths (typically 850, 1310, 1550 nm).

**Parameters:**
- `wavelength_nm` (float): Wavelength in nanometres

**Returns:**
- `bool`: True if command sent successfully

**Note:** Not all PM-4212 units support this command. Check your device manual.

**Example:**
```python
meter.set_wavelength(1550.0)
```

---

## GUI Application

The included GUI provides real-time monitoring of all 4 channels with:

- **Numeric displays** showing current power in dBm for each channel
- **Waveform plot** showing power history (last 100 readings) for all channels
- **Colour-coded** display matching each channel to its plot line
- **Configurable port** selection
- **Live updates** at 100 ms intervals
- **Connection management** with connect/disconnect button

### Running the GUI

```bash
python -m optokon.gui
```

### GUI Features

| Feature | Description |
|---------|-------------|
| Port input | Configure serial port (default: COM10) |
| Connect/Disconnect button | Toggle connection |
| Channel displays | Real-time power in dBm for channels 1–4 |
| Waveform chart | Scrolling history of last 100 samples |
| Colour coding | Red, Green, Blue, Yellow for channels 1–4 |

---

## Complete Example

Here's a comprehensive example demonstrating typical usage:

```python
from optokon_pm4212 import OptokonPM4212
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def monitor_power(port='COM10', duration=30):
    """
    Monitor optical power for a specified duration.

    Parameters:
        port: Serial port (e.g. 'COM10')
        duration: Monitoring duration in seconds
    """
    with OptokonPM4212(port=port) as meter:
        # Get device info
        device_info = meter.get_device_info()
        logger.info(f"Connected to: {device_info}")

        # Perform continuous reads
        logger.info(f"Monitoring for {duration} seconds...")
        readings = meter.continuous_read(
            duration_seconds=duration,
            interval_seconds=0.2
        )

        # Analyse results
        if readings:
            powers_ch1 = [p[0] for _, p in readings]
            avg_power = sum(powers_ch1) / len(powers_ch1)
            max_power = max(powers_ch1)
            min_power = min(powers_ch1)

            logger.info(f"Channel 1 statistics:")
            logger.info(f"  Average: {avg_power:.2f} dBm")
            logger.info(f"  Maximum: {max_power:.2f} dBm")
            logger.info(f"  Minimum: {min_power:.2f} dBm")

if __name__ == '__main__':
    monitor_power(port='COM10', duration=10)
```

## Serial Port Configuration

### Windows

Serial ports are typically named `COM1`, `COM2`, etc. Use Device Manager to find the correct port:

1. Right-click Computer → Manage
2. Go to Device Manager
3. Expand "Ports (COM & LPT)"
4. Find your USB-to-Serial device

### Linux

Serial ports are typically `/dev/ttyUSB0`, `/dev/ttyUSB1`, etc.

List available ports:

```bash
ls /dev/tty*
```

### macOS

Serial ports are typically `/dev/tty.usbserial-*`

List available ports:

```bash
ls /dev/tty.*
```

## Troubleshooting

### Connection Issues

**Problem:** `ConnectionError: Cannot open serial port COM10`

**Solutions:**
- Verify the correct serial port (see Serial Port Configuration above)
- Ensure device is powered on
- Check USB cable connections
- Try a different USB port
- Reinstall USB drivers if available

### No Power Readings

**Problem:** `read_power()` returns empty list

**Solutions:**
- Ensure device is connected with `is_connected()`
- Check serial port is correct
- Try increasing timeout: `OptokonPM4212(port='COM10', timeout=2.0)`
- Check device power LED

### Serial Timeout Errors

**Problem:** Readings time out or are intermittent

**Solutions:**
- Increase timeout value: `OptokonPM4212(timeout=2.0)`
- Reduce update interval in GUI
- Check USB cable quality (try a shorter/different cable)
- Close other applications using the serial port

---

## Logging

The package uses Python's standard `logging` module. Configure logging to see debug information:

```python
import logging

# Show all debug messages
logging.basicConfig(level=logging.DEBUG)

# Or configure just this package
logger = logging.getLogger('optokon_pm4212')
logger.setLevel(logging.DEBUG)
```

Log levels:
- `DEBUG`: Detailed information (commands sent, responses received)
- `INFO`: General information (connection status, readings)
- `WARNING`: Warning messages (invalid readings, timeouts)
- `ERROR`: Error messages (connection failures, read errors)

---

## Specifications

### Optokon PM-4212

- **Channels:** 4 independent power measurement channels
- **Wavelengths:** Typically 850, 1310, 1550 nm (device-dependent)
- **Measurement range:** Approximately −80 to +10 dBm
- **Connection:** Serial (RS-232 via USB converter)
- **Baudrate:** 19200 bps (Optokon standard)
- **Response time:** ~50 ms per channel

### Network Requirements

- Serial communication via COM port or USB-to-Serial converter
- No network or TCP/IP required

---

## Comparison with Original Implementation

Key improvements from the original standalone script:

| Feature | Original | This Package |
|---------|----------|--------------|
| Connection | Basic serial | Managed with error handling |
| Data parsing | Simple | Robust with error recovery |
| Error handling | Minimal | Comprehensive logging |
| Type hints | None | Full annotations |
| API | Functions | Class-based with methods |
| Logging | print() | Python logging module |
| Testing | None | Test-ready design |
| Documentation | None | Comprehensive |

---

## License

This code is based on and extends the original Optokon PM-4212 implementation. Refer to your device licence and documentation for usage terms.

## References

- Optokon PM-4212 User Manual
- PySerial documentation: https://pyserial.readthedocs.io/
- PyQt5 documentation: https://www.riverbankcomputing.com/software/pyqt/

## Support

For device-specific issues, consult the Optokon PM-4212 User Manual or contact your supplier.

For issues with this Python implementation:
1. Check serial port configuration
2. Verify device is powered on and connected
3. Review logging output for error messages
4. Ensure Python dependencies are installed correctly

---

**Note:** This implementation assumes the Optokon PM-4212 is properly configured and functioning. Refer to the device manual for initial setup and calibration procedures.
