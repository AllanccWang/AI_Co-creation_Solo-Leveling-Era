# 🍎 PoC Project: ESP32 Edge AI Classification System

## 🎯 Project Objective

This Proof-of-Concept (PoC) project aims to implement a lightweight edge AI decision-making system using the resource-constrained ESP32 microcontroller. By leveraging sensor fusion, it integrates real-time data from a color sensor and a weight sensor to classify objects based on predefined logic. The system then drives a servo motor to perform automated sorting, completing an intelligent closed-loop process: **Sense → Decide → Actuate**.

---

## 🛠️ Step-by-Step Implementation Guide

The project is divided into three main phases:

### Phase 1: Hardware Setup & Sensor Calibration

#### Step 1-1: Assembly & Circuit Wiring

- Use jumper wires and a breadboard to connect the following modules to the ESP32:
  - Color sensor
  - Load cell (weight sensor)
  - OLED display
  - Servo motor
- Build a stable sorting platform ensuring:
  - Objects can be securely placed on the load cell
  - The color sensor can read object color at close range

#### Step 1-2: Load Cell Calibration

- Write initialization and test code
- Perform multiple measurements using standard weights
- Adjust calibration factor and offset to ensure stable and accurate readings

#### Step 1-3: Color Sensor & OLED Testing

- Write code to read raw R/G/B values
- Test with three sample objects (red, blue, yellow)
- Display sensor data on OLED for verification

---

### Phase 2: Logic Implementation & Edge Decision-Making

#### Step 2-1: Define Classification Rules

- Set classification boundaries based on weight and color data

#### Step 2-2: Implement Edge Decision Tree Logic

- Integrate sensor input and actuator control code
- Apply IF-THEN-ELSE logic for object classification:

| Classification | Servo Angle | Buzzer Frequency |
|----------------|-------------|------------------|
| CLASS A (Heavy) | 180°        | High (1000 Hz)   |
| CLASS B (Light Red) | 90°     | Medium (500 Hz)  |
| CLASS C (Light Other) | 0°    | Low (250 Hz)     |

#### Step 2-3: Display Classification Result

- Show final classification (Class A/B/C) on the OLED screen

---

### Phase 3: Execution & Validation

#### Step 3-1: Servo Motor Test

- Independently test servo motor control code
- Verify accuracy and stability of angle commands

#### Step 3-2: Full PoC Cycle Test

- Place test samples and observe system response
- Record classification accuracy and execution time

#### Step 3-3: Final Evaluation

- Validate that sensor fusion logic outperforms single-sensor approaches
- Successfully demonstrate intelligent sorting on ESP32