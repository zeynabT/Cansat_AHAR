import smbus2
import time

# Constants for the CCS811
CCS811_I2C_ADDRESS = 0x5A
CCS811_STATUS = 0x00
CCS811_MEAS_MODE = 0x01
CCS811_ALG_RESULT_DATA = 0x02
CCS811_APP_START = 0xF4

# Initialize I2C (SMBus)
bus = smbus2.SMBus(1)

def ccs811_start():
    # Start the application
    bus.write_byte(CCS811_I2C_ADDRESS, CCS811_APP_START)
    time.sleep(0.1)

    # Set measurement mode (continuous measurement every second)
    bus.write_byte_data(CCS811_I2C_ADDRESS, CCS811_MEAS_MODE, 0x10)
    time.sleep(0.1)

def read_data():
    # Read 4 bytes of data from the ALG_RESULT_DATA register
    data = bus.read_i2c_block_data(CCS811_I2C_ADDRESS, CCS811_ALG_RESULT_DATA, 4)
    
    # Extract eCO2 and TVOC values
    eCO2 = (data[0] << 8) | data[1]
    TVOC = (data[2] << 8) | data[3]
    
    return eCO2, TVOC

def main():
    ccs811_start()
    while True:
        try:
            eCO2, TVOC = read_data()
            print(f"eCO2: {eCO2} ppm, TVOC: {TVOC} ppb")
            time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
