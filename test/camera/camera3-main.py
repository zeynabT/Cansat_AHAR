from picamera2 import Picamera2
from PIL import Image
import io
import time

def capture_and_compress_image(picam2,filename):         

    # Capture the image to a memory buffer
    image_buffer = io.BytesIO()
    picam2.capture_file(image_buffer, format='jpeg')
    
    # Seek to the beginning of the buffer
    image_buffer.seek(0)

    # Open image with PIL
    image = Image.open(image_buffer)
    image.save('main'+filename, format='jpeg', quality=100)
    # Save the image with the desired quality
    image.save(filename, format='jpeg', quality=80)

    

    print(f"Image saved as {filename}")

if __name__ == "__main__":
    filename = 'captured_image.jpg'
    # Initialize the camera
    picam2 = Picamera2()

    # Configure the camera for still images with specified resolution
    config = picam2.create_still_configuration(
        main={"size": (1920, 1080)}  # Set resolution to 1920x1080
    )
    picam2.configure(config)

    # Start the camera (without preview)
    picam2.start()
    i=1
    while(True):
        try:
            capture_and_compress_image(picam2,str(i)+filename)
            i=i+1
        except:
            # Stop the camera
            picam2.stop()
            print('stoped camera')
            break