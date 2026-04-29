"""
Example usage of the Optokon PM-4212 Python interface.

This script demonstrates various ways to use the OptokonPM4212 class.
"""

import logging
import time
from optokon_pm4212 import OptokonPM4212

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_basic_reading():
    """Example 1: Simple power reading."""
    logger.info("=== Example 1: Basic Power Reading ===")

    meter = OptokonPM4212(port='COM10')

    try:
        meter.connect()
        powers = meter.read_power()
        logger.info(f"Power readings: {powers}")

        # Print individual channels
        for i, power in enumerate(powers):
            logger.info(f"  Channel {i + 1}: {power:.2f} dBm")

    finally:
        meter.disconnect()


def example_context_manager():
    """Example 2: Using context manager (recommended)."""
    logger.info("=== Example 2: Context Manager Usage ===")

    with OptokonPM4212(port='COM10') as meter:
        # Get device info
        info = meter.get_device_info()
        logger.info(f"Device: {info}")

        # Read powers
        powers = meter.read_power()
        logger.info(f"Powers: {powers}")

        # Context manager automatically handles disconnection
    logger.info("Connection closed automatically")


def example_single_channel():
    """Example 3: Reading a single channel."""
    logger.info("=== Example 3: Single Channel Reading ===")

    with OptokonPM4212(port='COM10') as meter:
        try:
            for channel in range(1, 5):
                power = meter.read_single_channel(channel=channel)
                if power is not None:
                    logger.info(f"Channel {channel}: {power:.2f} dBm")
                else:
                    logger.warning(f"Channel {channel}: No response")
        except ValueError as e:
            logger.error(f"Invalid channel: {e}")


def example_continuous_monitoring():
    """Example 4: Continuous monitoring over time."""
    logger.info("=== Example 4: Continuous Monitoring ===")

    with OptokonPM4212(port='COM10') as meter:
        # Monitor for 10 seconds with 200ms interval
        readings = meter.continuous_read(
            duration_seconds=10.0,
            interval_seconds=0.2
        )

        logger.info(f"Collected {len(readings)} readings")

        # Analyse channel 1 data
        if readings:
            powers_ch1 = [p[0] for _, p in readings]
            avg = sum(powers_ch1) / len(powers_ch1)
            maximum = max(powers_ch1)
            minimum = min(powers_ch1)

            logger.info(f"Channel 1 statistics:")
            logger.info(f"  Average: {avg:.2f} dBm")
            logger.info(f"  Maximum: {maximum:.2f} dBm")
            logger.info(f"  Minimum: {minimum:.2f} dBm")
            logger.info(f"  Variation: {maximum - minimum:.2f} dBm")


def example_periodic_reads():
    """Example 5: Periodic readings in a loop."""
    logger.info("=== Example 5: Periodic Readings ===")

    meter = OptokonPM4212(port='COM10')

    try:
        meter.connect()
        logger.info("Starting periodic reads (press Ctrl+C to stop)")

        count = 0
        while count < 10:  # Do 10 reads for example
            powers = meter.read_power()
            if powers:
                logger.info(
                    f"Read {count + 1}: Ch1={powers[0]:7.2f} "
                    f"Ch2={powers[1]:7.2f} Ch3={powers[2]:7.2f} Ch4={powers[3]:7.2f} dBm"
                )
                count += 1
            else:
                logger.warning("Failed to read, retrying...")

            time.sleep(0.5)  # Wait 500ms between reads

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        meter.disconnect()


def example_with_error_handling():
    """Example 6: Robust error handling."""
    logger.info("=== Example 6: Error Handling ===")

    # Try to connect with proper error handling
    try:
        meter = OptokonPM4212(port='COM99')  # Invalid port for demo
        meter.connect()
    except ConnectionError as e:
        logger.error(f"Connection failed: {e}")
        logger.info("Attempting with correct port...")

        meter = OptokonPM4212(port='COM10')
        try:
            meter.connect()
            powers = meter.read_power()
            logger.info(f"Success! Powers: {powers}")
        except Exception as e:
            logger.error(f"Still failed: {e}")
        finally:
            meter.disconnect()


def example_wavelength_setting():
    """Example 7: Setting wavelength (if supported)."""
    logger.info("=== Example 7: Wavelength Setting ===")

    with OptokonPM4212(port='COM10') as meter:
        # Try to set wavelength
        success = meter.set_wavelength(1550.0)
        if success:
            logger.info("Wavelength set to 1550 nm")
            powers = meter.read_power()
            logger.info(f"Powers at 1550 nm: {powers}")
        else:
            logger.warning("Device may not support wavelength setting")


def example_connection_status():
    """Example 8: Checking connection status."""
    logger.info("=== Example 8: Connection Status ===")

    meter = OptokonPM4212(port='COM10')

    logger.info(f"Connected before connect(): {meter.is_connected()}")

    meter.connect()
    logger.info(f"Connected after connect(): {meter.is_connected()}")

    powers = meter.read_power()
    logger.info(f"Reading while connected: {powers}")

    meter.disconnect()
    logger.info(f"Connected after disconnect(): {meter.is_connected()}")


if __name__ == '__main__':
    """Run examples (uncomment the ones you want to test)."""

    # Uncomment the examples you want to run:
    # example_basic_reading()
    # example_context_manager()
    # example_single_channel()
    # example_continuous_monitoring()
    example_periodic_reads()
    # example_with_error_handling()
    # example_wavelength_setting()
    # example_connection_status()

    logger.info("Examples complete")
