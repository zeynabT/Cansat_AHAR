# In The Name Of Allah
import smbus2, time
import smbus
import time
import threading
from smbus2 import SMBus
from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250
from picamera2 import Picamera2
from PIL import Image
import io
import logging

logging.basicConfig(
        filename="app.log",
        encoding="utf-8",
        filemode="a",
        format="{asctime}-{levelname}-{message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        level=logging.INFO
    )
logger=logging.getLogger()
# vars
eCO2 = 0
TVOC = 0
pressure = 0
altitude = 0
cTemp = 0
accel_data = []
gyro_data = []
mag_data = []
temp_c = 0
humidity = 0
camera_path = ""

# Constants for the CCS811
CCS811_I2C_ADDRESS = 0x5A
CCS811_STATUS = 0x00
CCS811_MEAS_MODE = 0x01
CCS811_ALG_RESULT_DATA = 0x02
CCS811_APP_START = 0xF4


def air_quality_ccs811(bus):
    try:
        # Read 4 bytes of data from the ALG_RESULT_DATA register
        data = bus.read_i2c_block_data(CCS811_I2C_ADDRESS, CCS811_ALG_RESULT_DATA, 4)
        # Extract eCO2 and TVOC values
        eCO2_local = (data[0] << 8) | data[1]
        TVOC_local = (data[2] << 8) | data[3]
        return eCO2_local, TVOC_local
    except Exception as e:
        print(f"Error: {e}")


def get_pressure_mpl3115(bus):
    mpl_address = 0x60
    # MPL3115A2 address, 0x60(96)
    # Select control register, 0x26(38)
    # 		0xB9(185)	Active mode, OSR = 128, Altimeter mode
    bus.write_byte_data(mpl_address, 0x26, 0xB9)
    # MPL3115A2 address, 0x60(96)
    # Select data configuration register, 0x13(19)
    # 		0x07(07)	Data ready event enabled for altitude, pressure, temperature
    bus.write_byte_data(mpl_address, 0x13, 0x07)
    # MPL3115A2 address, 0x60(96)
    # Select control register, 0x26(38)
    # 		0xB9(185)	Active mode, OSR = 128, Altimeter mode
    bus.write_byte_data(mpl_address, 0x26, 0xB9)

    time.sleep(0.5)

    # MPL3115A2 address, 0x60(96)
    # Read data back from 0x00(00), 6 bytes
    # status, tHeight MSB1, tHeight MSB, tHeight LSB, temp MSB, temp LSB
    data = bus.read_i2c_block_data(mpl_address, 0x00, 6)

    # Convert the data to 20-bits
    tHeight = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
    temp = ((data[4] * 256) + (data[5] & 0xF0)) / 16
    altitude_local = tHeight / 16.0
    cTemp_local = temp / 16.0

    # MPL3115A2 address, 0x60(96)
    # Select control register, 0x26(38)
    # 		0x39(57)	Active mode, OSR = 128, Barometer mode
    bus.write_byte_data(0x60, 0x26, 0x39)

    time.sleep(0.5)

    # MPL3115A2 address, 0x60(96)
    # Read data back from 0x00(00), 4 bytes
    # status, pres MSB1, pres MSB, pres LSB
    data = bus.read_i2c_block_data(0x60, 0x00, 4)
    # TODO how to convert datasheet
    # Convert the data to 20-bits
    pres = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
    pressure_local = (pres / 4.0) / 1000.0

    return pressure_local, altitude_local, cTemp_local


def accelerometer_mpu(mpu):
    # Read the accelerometer, gyroscope, and magnetometer values
    accel_data_local = mpu.readAccelerometerMaster()
    gyro_data_local = mpu.readGyroscopeMaster()
    mag_data_local = mpu.readMagnetometerMaster()

    return accel_data_local, gyro_data_local, mag_data_local


def temperature_sht(bus):
    # آدرس I2C سنسور
    SHT35_ADDRESS = 0x44

    # دستورات برای خواندن دما و رطوبت از سنسور SHT35
    # دستور برای خواندن دما و رطوبت با دقت متوسط
    command = 0x2C06
    try:
        # ارسال دستور به سنسور
        bus.write_i2c_block_data(SHT35_ADDRESS, command >> 8, [command & 0xFF])

        # خواندن داده‌ها از سنسور
        data = bus.read_i2c_block_data(SHT35_ADDRESS, 0, 6)

        # تبدیل داده‌های خام به دما و رطوبت
        temp_c_local = ((data[0] * 256 + data[1]) * 175.0 / 65535) - 45
        humidity_local = (data[3] * 256 + data[4]) * 100.0 / 65535
        return temp_c_local, humidity_local
    except OSError as e:
        print(f"Error: {e}")


def capture_and_compress_image(picam2, filename):

    # Capture the image to a memory buffer
    image_buffer = io.BytesIO()
    picam2.capture_file(image_buffer, format="jpeg")

    # Seek to the beginning of the buffer
    image_buffer.seek(0)

    # Open image with PIL
    image = Image.open(image_buffer)
    image.save(filename + "main" + "jpg", format="jpeg", quality=100)
    # Save the image with the desired quality
    image.save(filename + "jpg", format="jpeg", quality=80)

    return filename + "jpg"


def change_vars(type_var, var):
    global eCO2
    global TVOC
    global pressure
    global altitude
    global cTemp
    global accel_data
    global gyro_data
    global mag_data
    global temp_c
    global humidity
    global camera_path
    logger.info('sensor {} get value {}'.format(type_var,var))
    if type_var == "eCO2":
        if int(var) < 20000:
            eCO2 = var
        return
    if type_var == "TVOC":
        if int(var) < 20000:
            TVOC = var
        return
    if type_var == "pressure":
        pressure = round(var,2)
        return
    if type_var == "altitude":
        if int(var) < 2000:
            altitude = round(var,2)
        return
    if type_var == "cTemp":
        if int(var) < 100:
            cTemp = round(var,2)
        return
    if type_var == "accel_data":
        accel_data = var
        return
    if type_var == "gyro_data":
        gyro_data = var
        return
    if type_var == "mag_data":
        mag_data = var
        return
    if type_var == "temp_c":
        if int(var) < 100:
            temp_c = round(var,2)
        return
    if type_var == "humidity":
        if int(var) < 100:
            humidity = var
        return
    if type_var == "camera":
        camera_path = var
        return


def nrf():
    # data make to send
    send_time = ("%s_" % round(time.time() - start_timer, 1))
    locationX = "%sLx_36.31130898586006" % send_time
    locationY = "%sLy_59.526375931025" % send_time
    Acceleration = "%sA_{}*{}*{}".format(accel_data[0],accel_data[1],accel_data[2]) % send_time
    Angular_acceleration = "%sZ_{}*{}*{}".format(gyro_data[0],gyro_data[1],gyro_data[2]) % send_time
    temp = "%sT_{}".format(temp_c) % send_time
    humedity = "%sH_{}".format(humedity) % send_time
    hight = "%sL_{}".format(altitude) % send_time
    presure = "%sP_{}".format(pressure) % send_time
    tvoc = "%sTV_{}".format(TVOC) % send_time
    eco2 = "%sCO_{}".format(eCO2) % send_time
    # uv = "%sU_{}".format(secrets.randbelow(250)) % send_time

    payloader = [locationX, locationY, Acceleration, hight, presure,
                    Angular_acceleration, temp, humedity,eco2,tvoc]

    # Convert each string to bytearray individually
    byte_arrays = [bytearray(word, 'utf-8') for word in payloader]

    for ba in byte_arrays:
        print(ba)
        
    while True:
        print(f"eCO2: {eCO2} ppm, TVOC: {TVOC} ppb")
        print("Pressure : %.2f kPa" % pressure)
        print("Altitude : %.2f m" % altitude)
        print("Temperature in Celsius  : %.2f C" % cTemp)
        print("Accelerometer:", accel_data)
        print("Gyroscope:", gyro_data)
        print("Magnetometer:", mag_data)
        print(f"Temperature: {temp_c:.2f} °C, Humidity: {humidity:.2f} %")
        print("last image path: ", camera_path)
        print("---------------------------------------")
        time.sleep(1)


if __name__ == "__main__":
    
    # Initialize I2C (SMBus)
    bus1 = smbus.SMBus(1)
    bus2 = smbus2.SMBus(1)

    logger.info("ConfigSensors")
    # Initialize the camera
    logger.info("Initialize the camera")
    picam2 = Picamera2()
    # Configure the camera for still images with specified resolution
    config = picam2.create_still_configuration(
        main={"size": (1920, 1080)}  # Set resolution to 1920x1080
    )
    picam2.configure(config)
    # Start the camera (without preview)
    picam2.start()

    # ccs811 config
    # Start the application
    logger.info("config ccs811")
    bus2.write_byte(CCS811_I2C_ADDRESS, CCS811_APP_START)
    time.sleep(0.1)
    # Set measurement mode (continuous measurement every second)
    bus2.write_byte_data(CCS811_I2C_ADDRESS, CCS811_MEAS_MODE, 0x10)
    time.sleep(0.1)

    # Create an MPU9250 instance
    logger.info("Create an MPU9250 instance")
    mpu = MPU9250(
        address_ak=AK8963_ADDRESS,
        address_mpu_master=MPU9050_ADDRESS_68,  # In case the MPU9250 is connected to another I2C device
        address_mpu_slave=None,
        bus=1,
        gfs=GFS_1000,
        afs=AFS_8G,
        mfs=AK8963_BIT_16,
        mode=AK8963_MODE_C100HZ,
    )
    # Configure the MPU9250
    mpu.configure()
    # edn config
    logger.info("start Thread nrf")
    x = threading.Thread(target=nrf, args=())
    x.start()
    i = 1
    filename = "images/captured_image"
    while True:
        try:
            eCO2_local, TVOC_local = air_quality_ccs811(bus2)
            change_vars("eCO2", eCO2_local)
            change_vars("TVOC", TVOC_local)

            pressure_local, altitude_local, cTemp_local = get_pressure_mpl3115(bus1)
            change_vars("pressure", pressure_local)
            change_vars("altitude", altitude_local)
            change_vars("cTemp", cTemp_local)

            accel_data, gyro_data, mag_data = accelerometer_mpu(mpu)
            change_vars("accel_data", accel_data)
            change_vars("gyro_data", gyro_data)
            change_vars("mag_data", mag_data)

            temp_c, humidity = temperature_sht(bus2)
            change_vars("temp_c", temp_c)
            change_vars("humidity", humidity)
        except Exception as e:
            print("some error:", e)
        try:
            path_file = capture_and_compress_image(picam2, filename + str(i))
            change_vars("camera", path_file)
            i = i + 1
        except:
            # Stop the camera
            picam2.stop()
            print("stoped camera")
            break
        time.sleep(1)
