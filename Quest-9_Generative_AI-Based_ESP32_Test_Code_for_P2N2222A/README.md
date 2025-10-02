# Goal
Build a scalable platform to automatically generate an Arduino test program for the P2N2222A NPN transistor using Generative AI (Gen AI), and here we choose P2N2222A switching functional test as an example.

# Quests
* *Phase 1: Project Organization:*
First task is to organize the necessary project documentation into a structured format to serve as the input for the Gen AI model.
project_root/
├─ circuit_interface(.md): Describes how the device is wired, including assignments and external components.
├─ spec(.md): Extracted electrical characteristics from the datasheet
├─ voltage_level(.csv): CSV file listing operating voltage ranges and current limits.
├─ pin_define(.json): Maps device pins to test platform pins
├─ test_flow(.yaml): Step-by-step test procedures
├─ Device datasheet

* *Phase 2: Code Generation:*
Your next objective is to use these structured documents as context for a Generative AI model to synthesize the final Arduino C++ test code. Target is to use prompts generate the P2N2222A_switching_test.cpp program.
