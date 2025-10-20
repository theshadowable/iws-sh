# IoT Device Integration Guide

## Overview
IndoWater supports real-time IoT device integration for water meters. This guide shows how to connect ESP32/Arduino devices to the system.

## Supported Protocols
- **HTTP POST** (Simple, recommended for beginners)
- **WebSocket** (Bidirectional communication)
- **MQTT** (Coming soon - for large-scale deployments)

---

## Quick Start: ESP32/Arduino Example

### 1. Hardware Requirements
- ESP32 or Arduino with WiFi shield
- Water flow sensor (YF-S201 or similar)
- Temperature sensor (DS18B20 - optional)
- Pressure sensor (optional)

### 2. Arduino/ESP32 Code Example

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// IndoWater backend
const char* serverUrl = "http://your-backend-url.com/api/iot/data/ingest";
const char* deviceId = "YOUR_DEVICE_ID";
const char* deviceSecret = "YOUR_DEVICE_SECRET";

// Sensor pins
const int flowSensorPin = 2;
const int tempSensorPin = 4;

// Variables
volatile int pulseCount = 0;
float flowRate = 0.0;
float totalVolume = 0.0;
unsigned long oldTime = 0;

void IRAM_ATTR pulseCounter() {
  pulseCount++;
}

void setup() {
  Serial.begin(115200);
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" Connected!");
  
  // Setup flow sensor
  pinMode(flowSensorPin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(flowSensorPin), pulseCounter, FALLING);
}

void loop() {
  // Calculate flow rate every second
  if ((millis() - oldTime) > 1000) {
    detachInterrupt(digitalPinToInterrupt(flowSensorPin));
    
    // Calculate flow rate (L/min)
    flowRate = ((1000.0 / (millis() - oldTime)) * pulseCount) / 7.5;
    oldTime = millis();
    
    // Calculate volume (L)
    float volumeConsumed = flowRate / 60.0;  // L/sec
    totalVolume += volumeConsumed;
    
    pulseCount = 0;
    attachInterrupt(digitalPinToInterrupt(flowSensorPin), pulseCounter, FALLING);
    
    // Send data every 5 seconds
    static unsigned long lastSend = 0;
    if (millis() - lastSend > 5000) {
      sendDataToServer();
      lastSend = millis();
    }
  }
}

void sendDataToServer() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-Device-Secret", deviceSecret);
    
    // Create JSON payload
    StaticJsonDocument<512> doc;
    doc["device_id"] = deviceId;
    doc["timestamp"] = getISOTimestamp();
    doc["flow_rate"] = flowRate;
    doc["volume_consumed"] = flowRate / 60.0;  // L in this reading
    doc["total_volume"] = totalVolume;
    doc["balance"] = 500000.0;  // Get from your local storage
    doc["valve_status"] = "open";
    doc["device_status"] = "online";
    doc["temperature"] = readTemperature();  // Implement this
    doc["battery_level"] = 100;  // If battery powered
    doc["signal_strength"] = WiFi.RSSI();
    doc["cost_per_liter"] = 10.0;
    
    String jsonString;
    serializeJson(doc, jsonString);
    
    int httpResponseCode = http.POST(jsonString);
    
    if (httpResponseCode > 0) {
      Serial.print("Data sent successfully: ");
      Serial.println(httpResponseCode);
      String response = http.getString();
      Serial.println(response);
    } else {
      Serial.print("Error sending data: ");
      Serial.println(httpResponseCode);
    }
    
    http.end();
  }
}

String getISOTimestamp() {
  // Simple timestamp - in production use RTC or NTP
  unsigned long seconds = millis() / 1000;
  char timestamp[32];
  sprintf(timestamp, "2025-01-15T%02d:%02d:%02dZ", 
          (int)((seconds / 3600) % 24),
          (int)((seconds / 60) % 60),
          (int)(seconds % 60));
  return String(timestamp);
}

float readTemperature() {
  // Implement temperature sensor reading
  // Example: DS18B20 reading
  return 25.0 + random(-3, 3);
}
```

### 3. Required Arduino Libraries
```
- WiFi (built-in for ESP32)
- HTTPClient (built-in for ESP32)
- ArduinoJson (install via Library Manager)
```

---

## Device Registration

### Step 1: Register Your Device

**HTTP POST** to `/api/iot/devices/register`

```bash
curl -X POST http://your-backend/api/iot/devices/register \
  -H "Content-Type: application/json" \
  -H "X-Device-Secret: your_device_secret" \
  -d '{
    "device_id": "ESP32-METER-001",
    "device_name": "Kitchen Water Meter",
    "device_type": "smart_meter",
    "connection_type": "http",
    "firmware_version": "v1.0.0",
    "hardware_version": "ESP32-v2",
    "mac_address": "AA:BB:CC:DD:EE:FF"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Device registered successfully",
  "device_id": "ESP32-METER-001",
  "device_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "mqtt_topic": "indowater/ESP32-METER-001",
  "status": "offline"
}
```

### Step 2: Send Data

**HTTP POST** to `/api/iot/data/ingest`

```bash
curl -X POST http://your-backend/api/iot/data/ingest \
  -H "Content-Type: application/json" \
  -H "X-Device-Secret: your_device_secret" \
  -d '{
    "device_id": "ESP32-METER-001",
    "timestamp": "2025-01-15T10:30:00Z",
    "flow_rate": 15.5,
    "volume_consumed": 0.25,
    "total_volume": 1250.75,
    "balance": 475000.0,
    "valve_status": "open",
    "device_status": "online",
    "temperature": 26.5,
    "pressure": 3.5,
    "battery_level": 85,
    "signal_strength": -45,
    "cost_per_liter": 10.0
  }'
```

---

## Data Format Specifications

### Device Reading Fields

| Field | Type | Unit | Required | Description |
|-------|------|------|----------|-------------|
| device_id | string | - | Yes | Unique device identifier |
| timestamp | ISO8601 | - | Yes | Reading timestamp |
| flow_rate | float | L/min | Yes | Current water flow rate |
| volume_consumed | float | L | Yes | Volume in this reading period |
| total_volume | float | L | Yes | Total cumulative volume |
| balance | float | IDR | Yes | Remaining balance |
| valve_status | string | - | Yes | "open" or "closed" |
| device_status | string | - | Yes | "online", "warning", "error" |
| temperature | float | °C | No | Water temperature |
| pressure | float | Bar | No | Water pressure |
| battery_level | int | % | No | Battery level (0-100) |
| signal_strength | int | dBm | No | WiFi signal strength |
| cost_per_liter | float | IDR/L | Yes | Cost per liter |

---

## Testing with Simulator

We provide a Python simulator for testing without real hardware:

```bash
cd /app/backend
python iot_simulator.py
```

This will simulate 3 devices sending data every 5 seconds.

---

## Viewing Real-time Data

1. Login to IndoWater dashboard
2. Navigate to **IoT Monitoring** page
3. Select your device from the list
4. View real-time charts and metrics

The dashboard automatically connects via WebSocket and receives real-time updates.

---

## Security Considerations

1. **Device Secret**: Keep your device secret secure. Never commit it to public repos.
2. **HTTPS**: Use HTTPS in production to encrypt data transmission.
3. **Authentication**: Each device must authenticate with its secret.
4. **Rate Limiting**: Avoid sending data more than once per second to prevent server overload.

---

## Troubleshooting

### Device Registration Fails
- Check if device_id is unique
- Verify X-Device-Secret header is included
- Check backend is accessible from device

### Data Not Appearing in Dashboard
- Verify device is registered
- Check device secret matches
- Ensure WebSocket connection is active (green indicator)
- Check browser console for errors

### High Latency
- Reduce sending frequency (recommend 5-10 seconds)
- Check WiFi signal strength
- Use local buffer and batch sends if needed

---

## Next Steps

1. ✅ Register your device
2. ✅ Send test data
3. ✅ View real-time dashboard
4. 🔄 Implement alert notifications
5. 🔄 Add device commands (valve control)
6. 🔄 Set up MQTT for better scalability

For questions or issues, contact support.
