#include "BLEDevice.h"

BLEClient* pClient;
BLERemoteCharacteristic* pChar;

const char* cb10_mac = "CB:10:**:**:**:**"; // Replace with your actual CB10 MAC address
const char* target_char_uuid = "0000fff2-****-****-****-00805f9*****";

void sendTest(const char* label, uint8_t* data, size_t len) {
  Serial.println("──────────────────────────────");
  Serial.print("Sending ");
  Serial.print(label);
  Serial.print(" (");
  Serial.print(len);
  Serial.println(" bytes)");

  try {
    pChar->writeValue(data, len, true);
    delay(500);
    pChar->writeValue(data, len, false);
    Serial.println("✅ Write succeeded");
  } catch (...) {
    Serial.println("Write failed");
  }

  delay(1500); // Give CB10 time to react
}

void setup() {
  Serial.begin(115200);
  BLEDevice::init("");

  Serial.println("🔗 Connecting to CB10...");
  pClient = BLEDevice::createClient();
  if (!pClient->connect(BLEAddress(cb10_mac))) {
    Serial.println("Connection failed");
    return;
  }

  Serial.println("✅ Connected to CB10");
  delay(1000);

  std::map<std::string, BLERemoteService*>* services = pClient->getServices();
  if (!services) {
    Serial.println("No services found");
    return;
  }

  for (auto const& servicePair : *services) {
    BLERemoteService* service = servicePair.second;
    std::map<std::string, BLERemoteCharacteristic*>* chars = service->getCharacteristics();

    for (auto const& charPair : *chars) {
      std::string charUUID = charPair.first;
      if (charUUID == target_char_uuid) {
        pChar = charPair.second;
        Serial.print("✅ Found target characteristic: ");
        Serial.println(charUUID.c_str());

        // Send test formats
        uint8_t cmd1[] = {'F'};
        sendTest("'F'", cmd1, sizeof(cmd1));

        uint8_t cmd2[] = {'F', '\n'};
        sendTest("'F\\n'", cmd2, sizeof(cmd2));

        uint8_t cmd3[] = {'F', '\r'};
        sendTest("'F\\r'", cmd3, sizeof(cmd3));

        uint8_t cmd4[] = {'F', '\r', '\n'};
        sendTest("'F\\r\\n'", cmd4, sizeof(cmd4));

        uint8_t cmd5[] = {'G', 'O'};
        sendTest("'GO'", cmd5, sizeof(cmd5));

        uint8_t cmd6[] = {'G', 'O', '\r', '\n'};
        sendTest("'GO\\r\\n'", cmd6, sizeof(cmd6));

        uint8_t cmd7[] = {'C', 'M', 'D', ':', 'G', 'O'};
        sendTest("'CMD:GO'", cmd7, sizeof(cmd7));

        uint8_t cmd8[] = {'C', 'M', 'D', ':', 'G', 'O', '\r', '\n'};
        sendTest("'CMD:GO\\r\\n'", cmd8, sizeof(cmd8));

        uint8_t cmd9[] = {0xA1, 0x01};
        sendTest("Raw bytes 0xA1 0x01", cmd9, sizeof(cmd9));

        uint8_t cmd10[] = {0x01};
        sendTest("Raw byte 0x01", cmd10, sizeof(cmd10));

        Serial.println("🧪 Test complete — observe motor response");
        return;
      }
    }
  }

  Serial.println("Target characteristic not found");
}

void loop() {}
