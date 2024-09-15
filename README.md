# Mini Smart Home System

### Introduction
This repository presents a Smart Home System focused on enhanced security and automation. It features a door sector with face recognition, password verification, and alert mechanisms, alongside an interior sector equipped with temperature and motion sensors. The system integrates advanced technology to deliver a user-friendly, secure, and convenient home automation solution.

![Proteus Schematic Design](https://i.imgur.com/r5diF4c.png)
![while testing](https://i.imgur.com/NjjyXkp.png)

### Features

- Face recognition for door control
- Password entry via Arduino keypad
- Control interface for managing passwords and database entries
- LDR for light level measurement
- Temperature sensor with RGB LED indicator
- Fan control via temperature sensor and L293D chip
- PIR sensor for occupancy detection
- Buzzer for incorrect password warning

### Components

- ATMEGA 8A
- Keypad 4x4
- Buzzers
- Temperature sensor (NTC Thermistor Module)
- PIR sensor
- LDR sensor
- RGB LED
- Motor + Fan Blades
- Driver L293D
- LED (lighting system)
- Servo motor
- Shift Register (74HC595N)
- Resistors
- Crystal 16 MHz

### Libraries Used

#### 1. **Computer Vision Section**:
   - **OpenCV**
   - **dlib**
   - **NumPy**
   - **pySerial**

#### 2. **Microcontroller Section**:
   - **Servo**
   - **Keypad**

