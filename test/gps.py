import serial
import time

def read_gps_data():
    # Configure the serial port
    ser = serial.Serial(
        port='/dev/serial0',  # Use the correct serial port
        baudrate=9600,        # Baud rate for the MC60
        timeout=1             # Timeout in seconds
    )

    try:
        # Give the module some time to initialize
        time.sleep(2)

        # Send a command to start GPS (if needed)
        ser.write(b'AT+QGPS=1\r')

        # Allow time for the GPS module to acquire signals
        time.sleep(2)

        # Read GPS data
        while True:
            line = ser.readline().decode('utf-8').strip()
            print(line)
            if line.startswith('$GNRMC'):  # Look for the RMC sentence
                print("RMC Sentence:", line)
                break  # Exit after finding one RMC sentence

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the serial connection
        ser.close()

if __name__ == "__main__":
    read_gps_data()

