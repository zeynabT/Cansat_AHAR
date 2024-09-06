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

temp_raw = ((data[4] << 8) | data[5]) >> 4
cTemp = temp_raw / 16.0  
fTemp = cTemp * 1.8 + 32 

print("Pressure : %.2f kPa" % pressure)
print("Temperature in Celsius : %.2f C" % cTemp)
print("Temperature in Fahrenheit : %.2f F" % fTemp)
