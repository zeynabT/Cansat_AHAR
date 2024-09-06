import smbus2
import time

# MPL3115A2 I2C address
MPL3115A2_ADDRESS = 0x60

# Registers
MPL3115A2_REGISTER_STATUS = 0x00
MPL3115A2_REGISTER_PRESSURE_MSB = 0x01
MPL3115A2_REGISTER_TEMP_MSB = 0x04
MPL3115A2_REGISTER_CONTROL = 0x26
MPL3115A2_REGISTER_DATA_CONFIG = 0x13

# Control register settings
MPL3115A2_CTRL_BAROMETER = 0x38  # Barometer mode
MPL3115A2_CTRL_ALTIMETER = 0xB8  # Altimeter mode
MPL3115A2_CTRL_TEMP = 0x07       # Temperature mode

# I2C bus
bus = smbus2.SMBus(1)

# Helper function to write to registers
def write_register(register, value):
    bus.write_byte_data(MPL3115A2_ADDRESS, register, value)

# Helper function to read multiple bytes from a register
def read_register(register, length):
    return bus.read_i2c_block_data(MPL3115A2_ADDRESS, register, length)

# Initialize the sensor in Altimeter mode
def init_mpl3115a2():
    write_register(MPL3115A2_REGISTER_CONTROL, MPL3115A2_CTRL_ALTIMETER)  # Altimeter mode
    write_register(MPL3115A2_REGISTER_DATA_CONFIG, 0x07)  # Enable pressure and temperature data flags

# Read altitude in meters
def read_altitude():
    data = read_register(MPL3115A2_REGISTER_PRESSURE_MSB, 3)
    altitude = ((data[0] << 16) | (data[1] << 8) | data[2]) >> 4
    return altitude / 16.0

# Read pressure in Pascals
def read_pressure():
    # Switch to barometer mode
    write_register(MPL3115A2_REGISTER_CONTROL, MPL3115A2_CTRL_BAROMETER)
    time.sleep(0.5)

    data = read_register(MPL3115A2_REGISTER_PRESSURE_MSB, 3)
    pressure = ((data[0] << 16) | (data[1] << 8) | data[2]) >> 4
    return pressure / 4.0

# Read temperature in degrees Celsius
def read_temperature():
    data = read_register(MPL3115A2_REGISTER_TEMP_MSB, 2)
    temperature = (data[0] << 8) | data[1]
    if temperature > 32767:
        temperature -= 65536
    return temperature / 256.0

def main():
    # Initialize the sensor
    init_mpl3115a2()

    try:
        while True:
            # Read altitude
            altitude = read_altitude()
            print(f"Altitude: {altitude:.2f} meters")

            # Read pressure
            pressure = read_pressure()
            print(f"Pressure: {pressure:.2f} Pa")

            # Read temperature
            temperature = read_temperature()
            print(f"Temperature: {temperature:.2f} °C")

            time.sleep(1)

    except KeyboardInterrupt:
        print("Program stopped")

if __name__ == "__main__":
    main()