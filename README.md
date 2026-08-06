# Virtual Instrument Cluster for Electric Vehicles — Hardware & Software Integration

Bachelor's thesis project — **National University of Science and Technology Politehnica Bucharest (ETTI)**, 2026[cite: 2]. End-to-end development of a digital dashboard for an electric vehicle testing platform, encompassing custom PCB design, CAN bus communication, and real-time GUI rendering[cite: 1, 2].

> **Tools:** Python · PyQt5 · CAN Bus · Raspberry Pi 4 · MCP2515 · TJA1050 | **Author:** Mario-Cosmin Curea[cite: 1, 2]

---

## Overview

This project focuses on the development and implementation of a custom digital instrument cluster for an electric vehicle (EV) testing platform[cite: 1, 2]. The system is designed to acquire, process, and graphically display critical operational parameters in real-time, such as electric motor speed, current, high-voltage battery state of charge (SOC), and thermal metrics[cite: 1, 2].

Unlike standard software-only dashboards, this project represents a complete hardware-software co-design[cite: 2]. It interfaces directly with the vehicle's internal network, capturing raw data from the Motor Controller and the Battery Management System (BMS) over a robust CAN bus architecture[cite: 1, 2]. 

## What I did

* **Hardware Architecture & Schematic Design:** Designed the complete electrical schematic for a custom CAN interface shield tailored for a Raspberry Pi 4[cite: 1, 2]. 
* **Custom PCB Design:** Engineered and routed the Printed Circuit Board (PCB) layout, ensuring signal integrity for high-speed digital lines and proper thermal dissipation for power components[cite: 1, 2].
* **Hardware Assembly:** Manually assembled the hardware by soldering all SMD and THT components, including a custom 12V-to-5V DC-DC buck converter (MP1584EN), a CAN controller (MCP2515), a CAN transceiver (TJA1050), and an I2C Real-Time Clock (PCF8563)[cite: 1, 2].
* **Software Development (Python/PyQt5):** Developed a multi-threaded Python application utilizing the `python-can` library for backend data parsing and PyQt5 for the frontend[cite: 1, 2]. The software decodes raw CAN frames (e.g., IDs 0x601, 0x602, 0x501) and dynamically updates the virtual gauges[cite: 2].
* **System Integration & Physical Testing:** Validated the complete end-to-end system on the physical EV testing workbench in the laboratory[cite: 1, 2]. I executed physical tests to verify electrical continuity, signal integrity, and live data rendering under continuous operational loads[cite: 1, 2].

## Key results

* Achieved stable and error-free communication with the EV platform's internal CAN network at a baud rate of 500 kbps[cite: 1, 2].
* The custom-built DC-DC converter delivered a stable **5.18V** output with a measured power efficiency of approximately **89%**[cite: 1, 2].
* Successfully implemented a low-latency graphical user interface capable of rendering motor RPM, current regeneration, and battery health simultaneously[cite: 1, 2].
* Packaged the final hardware assembly compactly, ensuring compatibility with the standard Raspberry Pi enclosure for mechanical protection[cite: 2].

## Repository Structure

* `/Hardware`: Contains the PCB layout, schematics, and manufacturing files for the custom interface shield.
* `/Software`: Python source code, including the multi-threaded backend and the PyQt5 frontend components.
* `/Docs`: Project presentation, functional block diagrams, and system architecture documentation.
