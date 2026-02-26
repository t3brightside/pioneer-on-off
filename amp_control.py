import serial
import time
import sys

PORT = '/dev/ttyACM0'
BAUD = 9600

def send_command():
    try:
        with serial.Serial(PORT, BAUD, timeout=1) as ser:
            time.sleep(2) # Wait for Arduino to boot
            
            print("Sending Double-Tap Power Command...")
            # Send '1', wait 200ms, send '1' again
            ser.write(b'1')
            time.sleep(0.2)
            ser.write(b'1')
            
            response = ser.readline().decode('utf-8').strip()
            print(f"Arduino: {response}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    send_command()