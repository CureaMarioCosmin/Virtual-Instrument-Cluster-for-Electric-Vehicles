# Virtual Instrument Cluster for Electric Vehicles — Hardware & Software Integration

Bachelor's thesis project — **National University of Science and Technology Politehnica Bucharest (ETTI)**, 2026. End-to-end development of a digital dashboard for an electric vehicle testing platform, encompassing custom PCB design, CAN bus communication, and real-time GUI rendering.

> **Tools:** Python · PyQt5 · CAN Bus · Raspberry Pi 4 · MCP2515 · TJA1050 | **Author:** Mario-Cosmin Curea

---

## Overview

This project focuses on the development and implementation of a custom digital instrument cluster for an electric vehicle (EV) testing platform. The system is designed to acquire, process, and graphically display critical operational parameters in real-time, such as electric motor speed, current, high-voltage battery state of charge (SOC), and thermal metrics.

Unlike standard software-only dashboards, this project represents a complete hardware-software co-design. It interfaces directly with the vehicle's internal network, capturing raw data from the Motor Controller and the Battery Management System (BMS) over a robust CAN bus architecture. 

## What I did

* **Hardware Architecture & Schematic Design:** Designed the complete electrical schematic for a custom CAN interface shield tailored for a Raspberry Pi 4. 
* **Custom PCB Design:** Engineered and routed the Printed Circuit Board (PCB) layout, ensuring signal integrity for high-speed digital lines and proper thermal dissipation for power components.
* **Hardware Assembly:** Manually assembled the hardware by soldering all SMD and THT components, including a custom 12V-to-5V DC-DC buck converter (MP1584EN), a CAN controller (MCP2515), a CAN transceiver (TJA1050), and an I2C Real-Time Clock (PCF8563).
* **Software Development (Python/PyQt5):** Developed a multi-threaded Python application utilizing the `python-can` library for backend data parsing and PyQt5 for the frontend. The software decodes raw CAN frames (e.g., IDs 0x601, 0x602, 0x501) and dynamically updates the virtual gauges.
* **System Integration & Physical Testing:** Validated the complete end-to-end system on the physical EV testing workbench in the laboratory. I executed physical tests to verify electrical continuity, signal integrity, and live data rendering under continuous operational loads.

## Key results

* Achieved stable and error-free communication with the EV platform's internal CAN network at a baud rate of 500 kbps.
* The custom-built DC-DC converter delivered a stable **5.18V** output with a measured power efficiency of approximately **89%**.
* Successfully implemented a low-latency graphical user interface capable of rendering motor RPM, current regeneration, and battery health simultaneously.
* Packaged the final hardware assembly compactly, ensuring compatibility with the standard Raspberry Pi enclosure for mechanical protection.

## Repository Structure

* `/Hardware`: Contains the PCB layout, schematics, and manufacturing files for the custom interface shield.
* `/Software`: Python source code, including the multi-threaded backend and the PyQt5 frontend components.
* `/Docs`: Project presentation, functional block diagrams, and system architecture documentation.
