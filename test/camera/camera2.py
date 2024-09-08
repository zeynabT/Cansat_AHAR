from picamera2 import Picamera2
import time

def capture_image(filename):
    picam2 = Picamera2()
    # تنظیمات پیش‌نمایش را به‌طور خاص غیرفعال کنید
    picam2.configure(picam2.create_still_configuration())
    picam2.start()
    time.sleep(1)  # زمان برای گرم شدن دوربین
    picam2.capture_file(filename)
    picam2.stop()

if __name__ == "__main__":
    output_file = 'captured_image.jpg'
    capture_image(output_file)

