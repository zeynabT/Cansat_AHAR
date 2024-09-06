from smbus2 import SMBus
import time

# آدرس I2C سنسور
SHT35_ADDRESS = 0x44

# دستورات برای خواندن دما و رطوبت از سنسور SHT35
def read_sht35(address):
    bus = SMBus(1)  # انتخاب باس I2C (معمولا 1)

    # دستور برای خواندن دما و رطوبت با دقت متوسط
    command = 0x2C06

    # ارسال دستور به سنسور
    bus.write_i2c_block_data(address, command >> 8, [command & 0xFF])

    # خواندن داده‌ها از سنسور
    data = bus.read_i2c_block_data(address, 0, 6)

    # تبدیل داده‌های خام به دما و رطوبت
    temp_c = ((data[0] * 256 + data[1]) * 175.0 / 65535) - 45
    humidity = ((data[3] * 256 + data[4]) * 100.0 / 65535) 

    return temp_c, humidity

if __name__ == "__main__":
    while True:
        try:
            temp, humi = read_sht35(SHT35_ADDRESS)
            print(f'Temperature: {temp:.2f} °C, Humidity: {humi:.2f} %')
        except OSError as e:
            print(f"Error: {e}")
        time.sleep(2)

