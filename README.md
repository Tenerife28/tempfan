# 🌀 TempFan: Smart Raspberry Pi Fan Controller

A robust, web-enabled PWM fan controller for Raspberry Pi. It monitors real-time temperatures using a DS18B20 sensor and dynamically adjusts fan speeds to ensure optimal cooling, while providing a sleek mobile-friendly web interface for remote monitoring and control.

## ✨ Key Features

* **Intelligent Auto Mode:** Automatically calculates and adjusts fan speed based on real-time temperature readings (customizable min/max temperature thresholds).
* **Responsive Web Dashboard:** A Flask-based web UI optimized for mobile devices. Monitor Temperature (°C), Fan Speed (RPM), and current Power (%) in real-time.
* **Manual Override & Haptics:** Seamlessly switch to Manual Mode and set exact fan speeds via a web slider. Includes haptic vibration feedback for mobile users.
* **🚀 Turbo Mode:** A 30-second 100% speed boost for rapid cooling. Can be triggered via the web interface or a physical hardware button.
* **Accurate RPM Tracking:** Reads the fan's tachometer pin using hardware interrupts for precise speed monitoring.

## 🛠️ Hardware Requirements

* Raspberry Pi
* 4-Pin PWM Fan (12V/5V depending on your setup, with tachometer)
* DS18B20 1-Wire Temperature Sensor
* Push Button (optional, for physical Turbo activation)
* Appropriate wiring/resistors (e.g., 4.7kΩ pull-up for the DS18B20)

## ⚙️ Prerequisites & Installation

1. **Enable 1-Wire on your Raspberry Pi:**
   You must enable the 1-Wire interface for the DS18B20 sensor to work.
   * Run `sudo raspi-config`
   * Go to `Interface Options` -> `1-Wire` and enable it.
   * Reboot your Pi.

2. **Clone the repository:**
   ```bash
   git clone https://github.com/Tenerife28/tempfan.git

