import smbus
import time

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

bus = smbus.SMBus(1)

def init_adxl345():
    bus.write_byte_data(ADXL345_ADDR, ADXL345_REG_POWER_CTL, 0x08)
    bus.write_byte_data(ADXL345_ADDR, ADXL345_REG_DATA_FORMAT, 0x08)

def read_acceleration():
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

    return {'x': x, 'y': y, 'z': z}

init_adxl345()

while True:
    try:
        accel_data = read_acceleration()
        print(f"X: {accel_data['x']} Y: {accel_data['y']} Z: {accel_data['z']}")
        time.sleep(1)

    except KeyboardInterrupt:
        print("Measurement stopped by user.")
        break
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(1)
