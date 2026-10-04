"""
================================================================================
  RASPBERRY PI TELEMETRY SENDER FOR THINGSPEAK & BLOOMBERG TERMINAL
================================================================================
  IoT Lab Python Script for Thonny IDE
  Channel ID:  3506638
  Write Key:   FNS56JJW80N89SY7

  Sensors Supported:
    - DHT11 / DHT22 (Temperature & Humidity)
    - HC-SR04 (Ultrasonic Distance Sensor)
================================================================================
"""

import time
import urllib.request
import urllib.parse

# Try importing Raspberry Pi GPIO (present on Raspberry Pi OS)
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("[WARN] RPi.GPIO not found. If running on your PC, dummy sensor test mode will be used.")

# Try importing Adafruit DHT library (if installed in Thonny)
try:
    import Adafruit_DHT
    DHT_AVAILABLE = True
except ImportError:
    DHT_AVAILABLE = False


# ==============================================================================
# 1. HARDWARE PIN CONFIGURATION (Modify to match your lab breadboard wiring)
# ==============================================================================
# Ultrasonic HC-SR04 Pins
TRIG_PIN = 23    # GPIO 23 (Pin 16) -> TRIG on HC-SR04
ECHO_PIN = 24    # GPIO 24 (Pin 18) -> ECHO on HC-SR04 (Use voltage divider!)

# DHT Sensor Configuration
DHT_PIN = 4      # GPIO 4  (Pin 7)  -> DATA pin on DHT11 / DHT22
DHT_TYPE = 11    # Set to 11 for DHT11, or 22 for DHT22 / AM2302

# ThingSpeak Credentials
THINGSPEAK_WRITE_KEY = "FNS56JJW80N89SY7"
THINGSPEAK_CHANNEL_ID = "3506638"
UPDATE_INTERVAL_SEC = 15  # ThingSpeak rate limit is minimum 15 seconds


# ==============================================================================
# 2. SENSOR READING FUNCTIONS
# ==============================================================================

def setup_gpio():
    """Initializes Raspberry Pi GPIO pins."""
    if not GPIO_AVAILABLE:
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.5)


def read_ultrasonic_distance():
    """
    Triggers the HC-SR04 ultrasonic sensor and calculates the distance in cm.
    Formula: Distance = (Sound Speed (343m/s) * Echo High Time) / 2
    """
    if not GPIO_AVAILABLE:
        # Fallback reading if testing without GPIO board
        return round(15.0 + (time.time() % 10), 1)

    try:
        # Trigger 10us ultrasonic pulse
        GPIO.output(TRIG_PIN, True)
        time.sleep(0.00001)
        GPIO.output(TRIG_PIN, False)

        pulse_start = time.time()
        pulse_end = time.time()

        timeout_start = time.time()
        while GPIO.input(ECHO_PIN) == 0:
            pulse_start = time.time()
            if pulse_start - timeout_start > 0.05:  # 50ms timeout
                return None

        while GPIO.input(ECHO_PIN) == 1:
            pulse_end = time.time()
            if pulse_end - pulse_start > 0.05:
                return None

        pulse_duration = pulse_end - pulse_start
        distance_cm = pulse_duration * 17150
        return round(distance_cm, 1)

    except Exception as e:
        print(f"  [!] Ultrasonic Read Error: {e}")
        return None


def read_dht_sensor():
    """
    Reads Temperature (°C) and Relative Humidity (%) from DHT11 or DHT22.
    """
    if DHT_AVAILABLE and GPIO_AVAILABLE:
        sensor_model = Adafruit_DHT.DHT11 if DHT_TYPE == 11 else Adafruit_DHT.DHT22
        humidity, temperature = Adafruit_DHT.read_retry(sensor_model, DHT_PIN)
        if temperature is not None and humidity is not None:
            return round(temperature, 1), round(humidity, 1)
        else:
            print("  [!] DHT read returned None. Retrying...")
            return None, None
    else:
        # Fallback if Adafruit_DHT is not yet installed in Thonny
        return None, None


# ==============================================================================
# 3. THINGSPEAK TRANSMISSION FUNCTION
# ==============================================================================

def send_to_thingspeak(temperature, humidity, distance):
    """
    Sends Field 1 (Temp), Field 2 (Humidity), and Field 3 (Distance)
    to ThingSpeak via HTTP GET request using Python's standard library.
    """
    params = {"api_key": THINGSPEAK_WRITE_KEY}

    if temperature is not None:
        params["field1"] = temperature
    if humidity is not None:
        params["field2"] = humidity
    if distance is not None:
        params["field3"] = distance

    query_string = urllib.parse.urlencode(params)
    url = f"https://api.thingspeak.com/update?{query_string}"

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'RaspberryPi-IoT-Station'})
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode('utf-8').strip()
            if result != "0":
                print(f"  [+] ThingSpeak ACK: Accepted (Entry ID #{result})")
                return True
            else:
                print("  [!] ThingSpeak Rejected: Rate limit active. Wait 15s before next update.")
                return False
    except Exception as e:
        print(f"  [-] Network Error: {e}")
        return False


# ==============================================================================
# 4. MAIN PROGRAM LOOP (RUN IN THONNY)
# ==============================================================================

def main():
    print("=" * 65)
    print("  BLOOMBERG TERMINAL IOT TELEMETRY NODE (RASPBERRY PI)")
    print(f"  Target Channel ID: {THINGSPEAK_CHANNEL_ID}")
    print(f"  Ultrasonic Pins:   TRIG=GPIO{TRIG_PIN}, ECHO=GPIO{ECHO_PIN}")
    print(f"  DHT Sensor Pin:    DATA=GPIO{DHT_PIN} (DHT{DHT_TYPE})")
    print(f"  Dashboard:         http://localhost:8080")
    print("=" * 65)

    setup_gpio()
    cycle = 1

    try:
        while True:
            print(f"\n--- [SAMPLE #{cycle} @ {time.strftime('%H:%M:%S')}] ---")

            # 1. Read Ultrasonic Distance
            distance = read_ultrasonic_distance()

            # 2. Read Temperature and Humidity
            temperature, humidity = read_dht_sensor()

            # Display readouts in Thonny Shell
            print(f"  Field 1 (Temperature): {temperature if temperature is not None else 'N/A'} °C")
            print(f"  Field 2 (Humidity):    {humidity if humidity is not None else 'N/A'} %")
            print(f"  Field 3 (Distance):    {distance if distance is not None else 'N/A'} cm")

            # 3. Transmit to ThingSpeak
            print("  Transmitting telemetry packet to ThingSpeak...")
            send_to_thingspeak(temperature, humidity, distance)

            cycle += 1
            print(f"  Sleeping {UPDATE_INTERVAL_SEC} seconds until next transmission...")
            time.sleep(UPDATE_INTERVAL_SEC)

    except KeyboardInterrupt:
        print("\n[STOP] Program stopped by user.")
    finally:
        if GPIO_AVAILABLE:
            GPIO.cleanup()
            print("[INFO] GPIO cleanup completed.")


if __name__ == "__main__":
    main()
