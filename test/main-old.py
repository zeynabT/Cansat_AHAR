
import smbus
import time
import RPi.GPIO as GPIO
import serial


# Acceleration
# ADXL345 I2C address
ADXL345_ADDR = 0x68

ADXL345_REG_DEVID = 0x00
ADXL345_REG_POWER_CTL = 0x2D
ADXL345_REG_DATA_FORMAT = 0x31
ADXL345_REG_DATAX0 = 0x32
ADXL345_REG_DATAX1 = 0x33
ADXL345_REG_DATAY0 = 0x34
ADXL345_REG_DATAY1 = 0x35
ADXL345_REG_DATAZ0 = 0x36
ADXL345_REG_DATAZ1 = 0x37
# End acceleration


def buzzer():

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.OUT)

    # Test Buzzer
    GPIO.output(4, GPIO.HIGH)  
    time.sleep(1) 
    GPIO.output(4, GPIO.LOW) 

    GPIO.cleanup()


def get_temperature_pressure():
    bus = smbus.SMBus(1)
    # Sensor I2C address
    ADDR = 0x68

    bus.write_byte_data(ADDR, 0x26, 0x39)
    bus.write_byte_data(ADDR, 0x13, 0x07)
    time.sleep(1) 

    data = bus.read_i2c_block_data(ADDR, 0x00, 6)

    pres_raw = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
    pressure = pres_raw / 8.0 / 1000.0  

    temp_raw = ((data[4] << 8) | data[5]) >> 4
    cTemp = temp_raw / 16.0  
    fTemp = cTemp * 1.8 + 32 

    print("Pressure : %.2f kPa" % pressure)
    print("Temperature in Celsius : %.2f C" % cTemp)
    print("Temperature in Fahrenheit : %.2f F" % fTemp)

    return {'temperature':cTemp,'pressure':pressure}




def read_acceleration():
    bus = smbus.SMBus(1)
    bus.write_byte_data(ADXL345_ADDR, ADXL345_REG_POWER_CTL, 0x08)
    bus.write_byte_data(ADXL345_ADDR, ADXL345_REG_DATA_FORMAT, 0x08)
    time.sleep(1)

    try:
        accel_data = read_acceleration()
        time.sleep(1)

        x0 = bus.read_byte_data(ADXL345_ADDR, ADXL345_REG_DATAX0)
        x1 = bus.read_byte_data(ADXL345_ADDR, ADXL345_REG_DATAX1)
        y0 = bus.read_byte_data(ADXL345_ADDR, ADXL345_REG_DATAY0)
        y1 = bus.read_byte_data(ADXL345_ADDR, ADXL345_REG_DATAY1)
        z0 = bus.read_byte_data(ADXL345_ADDR, ADXL345_REG_DATAZ0)
        z1 = bus.read_byte_data(ADXL345_ADDR, ADXL345_REG_DATAZ1)
        
        x = (x1 << 8) | x0
        y = (y1 << 8) | y0
        z = (z1 << 8) | z0

        if x > 32767:
            x -= 65536
        if y > 32767:
            y -= 65536
        if z > 32767:
            z -= 65536
        print(f"X: {accel_data['x']} Y: {accel_data['y']} Z: {accel_data['z']}")
        return {'x': x, 'y': y, 'z': z}

    except KeyboardInterrupt:
        print("Measurement stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(1)




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
                return {'gps':line}
                # break  # Exit after finding one RMC sentence

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the serial connection
        ser.close()

if __name__ == "__main__":
    buzzer()
    get_temperature_pressure()
    read_acceleration()
    read_gps_data()