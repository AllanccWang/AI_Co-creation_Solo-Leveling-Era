# Goal
Build a scalable platform that uses Generative AI (Gen AI) to automatically generate Arduino test programs for various electronic components and circuits.
ESP32 users can find a detailed reference implementation in this [_Link_](https://github.com/AllanccWang/electronic_projects/blob/5ac1c9ca14842814d4560cc3d93fe3264fc66a75/LAB14_Verify_P2N2222A_Amplifier-Transistor_Switching/README.md)

NOTICE: The project is currently in the optimization phase, with validation efforts actively underway to ensure performance and reliability.
# Quests
* *Phase 1: Project Organization:*
The first task is to organize the necessary project documentation into a structured format to serve as input for the Gen AI model. You need to gather and structure the following files for the P2N2222A transistor (one-time setup):
```yaml
project_root/
├─ circuit_interface(.md): Describes how the device is wired, including assignments and external components.
├─ spec(.md): Extracted electrical characteristics from the datasheet
├─ voltage_level(.csv): CSV file listing operating voltage ranges and current limits.
├─ pin_define(.json): Maps device pins to test platform pins
├─ test_flow(.yaml): Step-by-step test procedures
├─ Device datasheet
```
* *Phase 2: Code Generation:*
Your next objective is to use these structured documents as context for a Generative AI model to synthesize the final Arduino C++ test code. Target is to use prompts generate the P2N2222A_switching_test.cpp program.

* *Phase 3: Flash and Verify ESP32 Test Code*
Your next objective is to transition from the digital realm (generated code) to the physical realm (hardware validation). Goal is to upload the generated program to the ESP32 and prove that the test program is effective by forcing both PASS and FAIL conditions, where failure condition includes “Force the "ON State" Test to Fail” and “Force the "OFF State" Test to Fail”.

* *Phase 4: Expand Verification to Additional Components and Circuits*
I will verify additional components and circuits and post the results in the repository.
