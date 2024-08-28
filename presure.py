import smbus
import time

bus = smbus.SMBus(1)

# Sensor I2C address
ADDR = 0x68

bus.write_byte_data(ADDR, 0x26, 0x39)
bus.write_byte_data(ADDR, 0x13, 0x07)
time.sleep(1)

data = bus.read_i2c_block_data(ADDR, 0x00, 6)

pres_raw = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
pressure = pres_raw / 8.0 / 1000.0 

print("Pressure : %.2f kPa" % pressure)
