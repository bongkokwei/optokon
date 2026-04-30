"""
Optokon PM-4212 Live Monitor GUI

A PyQt5-based graphical interface for real-time monitoring of optical power
from an Optokon PM-4212 power meter with 4-channel display and live plotting.
"""

import sys
import time
import logging
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QFrame,
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

from .optokon_PM4212 import OptokonPM4212

# Configure logging
logger = logging.getLogger(__name__)


class PowerMeterGUI(QWidget):
    """
    Live monitoring GUI for Optokon PM-4212 optical power meter.

    Features:
    - Real-time power display for 4 channels
    - Live waveform plotting with scrolling history
    - Configurable serial port and update interval
    - Colour-coded display for each channel
    """

    # Display parameters
    MAX_HISTORY_POINTS = 100
    DEFAULT_PORT = "COM10"
    UPDATE_INTERVAL_MS = 100  # Update interval in milliseconds
    NOISE_FLOOR = -80.0  # dBm

    # Channel colours (RGBA)
    CHANNEL_COLOURS = [
        "#FF5555",  # Red
        "#55FF55",  # Green
        "#5555FF",  # Blue
        "#FFB555",  # Orange
    ]

    def __init__(self):
        """Initialise the GUI application."""
        super().__init__()
        logger.info("Initialising PowerMeterGUI")

        self.meter = OptokonPM4212(self.DEFAULT_PORT)
        self.setMaximumHeight(200)
        self.setMaximumWidth(600)

        # Data storage for the chart (scrolling history)
        self.data_history = [np.zeros(self.MAX_HISTORY_POINTS) for _ in range(4)]
        self.ptr = 0

        self.initUI()

        # Timer for periodic updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all)

        logger.debug("GUI initialisation complete")

    def initUI(self):
        """Construct the user interface."""
        self.setWindowTitle("Optokon PM-4212 Live Monitor")
        self.resize(1000, 700)
        main_layout = QHBoxLayout()

        # --- LEFT PANEL: Controls & Numeric Displays ---
        left_panel = QVBoxLayout()

        # Connection control area
        conn_layout = QHBoxLayout()
        self.port_input = QLineEdit(self.DEFAULT_PORT)
        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(QLabel("Port:"))
        conn_layout.addWidget(self.port_input)
        conn_layout.addWidget(self.btn_connect)
        left_panel.addLayout(conn_layout)

        # Digital power displays for each channel
        logger.debug("Creating channel display widgets")
        self.channel_labels = []
        for i in range(4):
            frame = QFrame()
            frame.setFrameShape(QFrame.Box)
            frame.setLineWidth(2)
            f_layout = QVBoxLayout(frame)

            # Channel label
            label = QLabel(f"PORT {i + 1}")
            label.setFont(QFont("Arial", 12, QFont.Bold))

            # Power value display
            val = QLabel(f"{self.NOISE_FLOOR:.2f} dBm")
            val.setFont(QFont("Courier", 24, QFont.Bold))
            val.setStyleSheet(f"color: {self.CHANNEL_COLOURS[i]};")

            f_layout.addWidget(label)
            f_layout.addWidget(val)
            self.channel_labels.append(val)
            left_panel.addWidget(frame)

        left_panel.addStretch()
        main_layout.addLayout(left_panel, 1)

        # --- RIGHT PANEL: Live Waveform Chart ---
        logger.debug("Creating waveform plot")
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground("k")  # Black background
        self.graphWidget.showGrid(x=True, y=True, alpha=0.3)
        self.graphWidget.setLabel("left", "Power", units="dBm")
        self.graphWidget.setLabel("bottom", "Sample")
        self.graphWidget.setYRange(-60, 10)  # Typical Optokon range
        self.graphWidget.setTitle("Real-time Power Monitor")

        # Create plot curves for the 4 ports
        self.curves = []
        for i in range(4):
            curve = self.graphWidget.plot(
                pen=pg.mkPen(self.CHANNEL_COLOURS[i], width=2)
            )
            self.curves.append(curve)

        main_layout.addWidget(self.graphWidget, 3)
        self.setLayout(main_layout)

        logger.debug("UI construction complete")

    def toggle_connection(self):
        """Toggle connection to the device."""
        if self.timer.isActive():
            # Currently connected - disconnect
            self.timer.stop()
            self.meter.disconnect()
            self.btn_connect.setText("Connect")
            self.port_input.setEnabled(True)
            logger.info("Disconnected from device")
        else:
            # Not connected - attempt connection
            port = self.port_input.text()
            self.meter = OptokonPM4212(port)

            try:
                if self.meter.connect():
                    # Get device info
                    info = self.meter.get_device_info()
                    logger.info(f"Connected to device: {info}")

                    self.btn_connect.setText("Disconnect")
                    self.port_input.setEnabled(False)
                    self.timer.start(self.UPDATE_INTERVAL_MS)  # Update every 100ms
                else:
                    self.port_input.setText("ERROR")
                    logger.error(f"Failed to connect to {port}")
            except Exception as e:
                logger.error(f"Connection error: {e}")
                self.port_input.setText("ERROR")

    def update_all(self):
        """Update all display elements with latest readings."""
        try:
            readings = self.meter.read_power()

            if readings and len(readings) >= 4:
                # Update numeric displays and waveform
                for i in range(4):
                    val = readings[i]

                    # Update text display
                    self.channel_labels[i].setText(f"{val:.2f} dBm")

                    # Update data buffer (roll values to the left)
                    self.data_history[i] = np.roll(self.data_history[i], -1)
                    self.data_history[i][-1] = val

                    # Update chart curve
                    self.curves[i].setData(self.data_history[i])

                logger.debug(f"Updated displays: {readings}")
            else:
                logger.warning(f"Invalid reading: {readings}")

        except Exception as e:
            logger.error(f"Error updating display: {e}")


def main():
    """Main entry point for the GUI application."""
    # Configure logging
    logging.basicConfig(
        level=logging.CRITICAL + 1,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Starting Optokon PM-4212 Live Monitor")

    app = QApplication(sys.argv)
    window = PowerMeterGUI()
    window.show()

    logger.info("GUI window displayed")
    exit_code = app.exec_()

    logger.info(f"Application exiting with code {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
