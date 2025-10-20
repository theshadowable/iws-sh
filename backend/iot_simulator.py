"""
IoT Device Simulator
Simulates real IoT devices sending data for testing purposes
"""
import asyncio
import random
import httpx
import json
from datetime import datetime
import hashlib

# Simulator Configuration
BACKEND_URL = "http://localhost:8001"
DEVICE_SECRET = "simulator_secret_key_2025"

# Simulated Devices
SIMULATED_DEVICES = [
    {
        "device_id": "SIM-METER-001",
        "device_name": "Simulator Smart Meter 1",
        "firmware_version": "v1.0.0",
        "hardware_version": "ESP32-v2",
        "mac_address": "AA:BB:CC:DD:EE:01",
        "base_flow_rate": 15.0,  # Base flow rate L/min
        "variation": 5.0  # Random variation
    },
    {
        "device_id": "SIM-METER-002",
        "device_name": "Simulator Smart Meter 2",
        "firmware_version": "v1.0.0",
        "hardware_version": "ESP32-v2",
        "mac_address": "AA:BB:CC:DD:EE:02",
        "base_flow_rate": 25.0,
        "variation": 10.0
    },
    {
        "device_id": "SIM-METER-003",
        "device_name": "Simulator Smart Meter 3",
        "firmware_version": "v1.0.0",
        "hardware_version": "Arduino-Mega",
        "mac_address": "AA:BB:CC:DD:EE:03",
        "base_flow_rate": 8.0,
        "variation": 3.0
    }
]


class IoTDeviceSimulator:
    """Simulates an IoT water meter device"""
    
    def __init__(self, device_config):
        self.config = device_config
        self.total_volume = 0.0
        self.balance = 500000.0  # Start with 500k IDR
        self.valve_status = "open"
        self.battery_level = 100
        self.is_running = False
        
    async def register(self):
        """Register device with backend"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{BACKEND_URL}/api/iot/devices/register",
                    json={
                        "device_id": self.config["device_id"],
                        "device_name": self.config["device_name"],
                        "device_type": "smart_meter",
                        "connection_type": "http",
                        "firmware_version": self.config["firmware_version"],
                        "hardware_version": self.config["hardware_version"],
                        "mac_address": self.config["mac_address"]
                    },
                    headers={"X-Device-Secret": DEVICE_SECRET},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Device {self.config['device_id']} registered: {result.get('message')}")
                    return True
                else:
                    print(f"❌ Registration failed for {self.config['device_id']}: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Registration error for {self.config['device_id']}: {e}")
                return False
    
    def generate_reading(self):
        """Generate realistic sensor reading"""
        # Simulate flow rate with random variation
        base = self.config["base_flow_rate"]
        variation = self.config["variation"]
        
        # Add some patterns (higher during day, lower at night)
        hour = datetime.now().hour
        time_factor = 1.0
        if 22 <= hour or hour <= 6:  # Night time - lower flow
            time_factor = 0.3
        elif 6 < hour <= 9 or 17 <= hour <= 20:  # Peak hours
            time_factor = 1.5
        
        flow_rate = max(0, base * time_factor + random.uniform(-variation, variation))
        
        # Volume consumed in this reading (assume 1 minute interval)
        volume_consumed = flow_rate * 1.0  # L/min * 1 min
        self.total_volume += volume_consumed
        
        # Calculate cost and deduct from balance
        cost = volume_consumed / 1000 * 10000  # Convert to m³ and multiply by rate
        self.balance = max(0, self.balance - cost)
        
        # Simulate battery drain (very slow)
        if random.random() < 0.01:  # 1% chance per reading
            self.battery_level = max(0, self.battery_level - 1)
        
        # Simulate temperature and pressure
        temperature = 25 + random.uniform(-3, 3)  # Celsius
        pressure = 3.5 + random.uniform(-0.5, 0.5)  # Bar
        
        # Simulate signal strength
        signal_strength = random.randint(-70, -40)  # dBm
        
        # Determine device status
        device_status = "online"
        if self.balance < 10000:
            device_status = "warning"  # Low balance
        if self.battery_level < 15:
            device_status = "warning"  # Low battery
        
        return {
            "device_id": self.config["device_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "flow_rate": round(flow_rate, 2),
            "volume_consumed": round(volume_consumed, 2),
            "total_volume": round(self.total_volume, 2),
            "balance": round(self.balance, 2),
            "valve_status": self.valve_status,
            "device_status": device_status,
            "temperature": round(temperature, 1),
            "pressure": round(pressure, 2),
            "battery_level": self.battery_level,
            "signal_strength": signal_strength,
            "cost_per_liter": 10.0
        }
    
    async def send_reading(self):
        """Send reading to backend"""
        reading = self.generate_reading()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{BACKEND_URL}/api/iot/data/ingest",
                    json=reading,
                    headers={"X-Device-Secret": DEVICE_SECRET},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    print(f"📊 {self.config['device_id']}: Flow={reading['flow_rate']}L/min, "
                          f"Balance=Rp{reading['balance']:,.0f}, Battery={reading['battery_level']}%")
                    return True
                else:
                    print(f"❌ Failed to send reading from {self.config['device_id']}: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error sending reading from {self.config['device_id']}: {e}")
                return False
    
    async def run(self, interval_seconds=5):
        """Run simulator continuously"""
        print(f"🚀 Starting simulator for {self.config['device_id']}...")
        
        # Register first
        registered = await self.register()
        if not registered:
            print(f"⚠️  Failed to register {self.config['device_id']}, but continuing anyway...")
        
        self.is_running = True
        
        while self.is_running:
            await self.send_reading()
            await asyncio.sleep(interval_seconds)
    
    def stop(self):
        """Stop simulator"""
        self.is_running = False


async def run_all_simulators(interval_seconds=5):
    """Run all simulated devices"""
    print("=" * 80)
    print("🌊 IndoWater IoT Simulator")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Number of devices: {len(SIMULATED_DEVICES)}")
    print(f"Reading interval: {interval_seconds} seconds")
    print("=" * 80)
    print()
    
    # Create simulators
    simulators = [IoTDeviceSimulator(device) for device in SIMULATED_DEVICES]
    
    # Run all simulators concurrently
    tasks = [sim.run(interval_seconds) for sim in simulators]
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\n⏹️  Stopping all simulators...")
        for sim in simulators:
            sim.stop()


if __name__ == "__main__":
    try:
        asyncio.run(run_all_simulators(interval_seconds=5))
    except KeyboardInterrupt:
        print("\n✅ Simulator stopped")
