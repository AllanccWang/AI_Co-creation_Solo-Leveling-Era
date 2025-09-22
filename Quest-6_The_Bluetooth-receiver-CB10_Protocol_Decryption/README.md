# Goal
The primary objective is to reverse-engineer the communication protocol of the CB10 Bluetooth receiver. 
This will allow you to bypass the mobile app and connect the receiver directly to an ESP32 microcontroller, 
a critical first step in a larger project to integrate sensors with your LEGO Power Functions (9686 series) models.
# Quests
* Side Quest 1: Target Identification
    - **Objective:** Confirm that the CB10 Bluetooth receiver is a Bluetooth Low Energy (BLE) device.
    - **Task:** Identify the CB10's MAC address and its discoverable characteristics to prepare for a connection.
* Side Quest 2: Command Trial
    - **Objective:** Use your **Program Development** skill to test different common BLE command formats to see if the CB10 responds. This will give you preliminary clues about the protocol.
    - **Task:** Implement and send various test commands to the receiver.
* Side Quest 3: Protocol Reconnaissance
    - **Objective:** Determine if the CB10 uses a standard Serial Port Profile (SPP) or a Bluetooth Low Energy (BLE) UART protocol. This information is crucial for your communication strategy.
    - **Task:** Probe the device to identify the communication mode.
* Side Quest 4: Packet Interception
    - **Objective:** Propose a method to intercept the communication between the original mobile app and the CB10. This is a classic Information Retrieval quest.
    - **Task:** Propose using a BLE Sniffer tool, such as an nRF52840, in combination with a tool like Wireshark, to capture the packets.
# Strategic Evaluation
- Weigh the time and effort required for the decoding against the project's ultimate purpose to determine if this is the most effective path forward. This quest highlights your ability to pivot and make strategic decisions.
