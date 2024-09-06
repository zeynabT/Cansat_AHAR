import cv2
import numpy as np 

class ShapeDetector:
    def __init__(self):
        pass

    def detect(self, c):

        shape = "unidentified"
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)

        if len(approx) == 3:
            shape = "triangle"
        
        elif len(approx) == 4:
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w / float(h)
            shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"

        else:
            area = cv2.contourArea(c)
            if area == 0:
                return shape
            circularity = (4 * np.pi * area) / (peri * peri)
            shape = "circle" if circularity > 0.8 else "polygon"

        return shape
