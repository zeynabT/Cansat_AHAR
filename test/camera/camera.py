# libcamera-jpeg -o image.jpg --quality 85 --width 1920 --height 1080


import os,time 
i=1
while True:
    os.system('libcamera-jpeg -o image{}.jpg --quality 85 --width 1920 --height 1080'.format(i))
    print('image{}.jpg'.format(i))
    i=i+1
    time.sleep(1)
   