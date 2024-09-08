import serial

ser = serial.Serial(
    port='/dev/ttyAMA0',  # Use the correct serial port
    baudrate=115200,        # Baud rate for the MC60
    timeout=1           # Timeout in seconds
)
ser.write(b'AT\n')

while True:
    line = ser.readline().decode('utf-8').strip()
    print(line)