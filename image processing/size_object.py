from shapedetector import ShapeDetector
import numpy as np
import imutils
import cv2
import pandas as pd
from imutils import perspective
from imutils import contours

def show_images(images):
    for i, img in enumerate(images):
        cv2.namedWindow("image_" + str(i), cv2.WINDOW_NORMAL)
        cv2.imshow("image_" + str(i), img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def get_color(r, g, b, csv):
    minimum = 10000
    color_name = "Unknown"
    for index in range(len(csv)):
        distance = abs(r - int(csv.loc[index, "r"])) + abs(g - int(csv.loc[index, "g"])) + abs(b - int(csv.loc[index, "b"]))
        if distance <= minimum:
            minimum = distance
            color_name = csv.loc[index, 'color_name']
    return color_name

def calculate_area(shape, cnt, pixel_per_m):
    if shape == "circle":
        _, radius = cv2.minEnclosingCircle(cnt)
        area_in_pixels = np.pi * (radius ** 2)
    elif shape == "triangle":
        approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
        side_a = np.linalg.norm(approx[0] - approx[1])
        side_b = np.linalg.norm(approx[1] - approx[2])
        side_c = np.linalg.norm(approx[2] - approx[0])
        s = (side_a + side_b + side_c) / 2
        area_in_pixels = np.sqrt(s * (s - side_a) * (s - side_b) * (s - side_c))
    else:
        area_in_pixels = cv2.contourArea(cnt)
    
    area_in_m2 = area_in_pixels / (pixel_per_m ** 2)
    return area_in_m2

img_path = "./image processing/image/10_3-68-609.jpg"
real_world_height_in_m = 3.7  # Real-world height of the scene

image = cv2.imread(img_path)

if image is None:
    print("Error: Unable to load the image.")
else:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9, 9), 0)

    edged = cv2.Canny(blur, 50, 100)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)

    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    (cnts, _) = contours.sort_contours(cnts)

    cnts = [x for x in cnts if cv2.contourArea(x) > 100]

    if len(cnts) == 0:
        print("No contours found.")
        exit()

    # Image dimensions
    image_height_in_pixels = image.shape[0]
    image_width_in_pixels = image.shape[1]

    # Calculate real-world width based on aspect ratio
    real_world_width_in_m = real_world_height_in_m * (4 / 3)

    # Calculate pixel-per-meter for both dimensions
    pixel_per_m_height = image_height_in_pixels / real_world_height_in_m
    pixel_per_m_width = image_width_in_pixels / real_world_width_in_m

    # Average pixel-per-meter ratio
    pixel_per_m = (pixel_per_m_height + pixel_per_m_width) / 2

    header = ['color', 'color_name', 'hexa', 'r', 'g', 'b']
    csv = pd.read_csv('./image processing/colors.csv', names=header, header=0)

    sd = ShapeDetector()

    for cnt in cnts:
        shape = sd.detect(cnt)

        # Draw contours in red for visual inspection
        cv2.drawContours(image, [cnt], -1, (0, 0, 255), 2)

        # Calculate area and handle shapes
        if shape == "circle":
            ((x, y), radius) = cv2.minEnclosingCircle(cnt)
            center = (int(x), int(y))
            radius = int(radius)
            cv2.circle(image, center, radius, (0, 255, 0), 2)
        elif shape == "triangle":
            approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
            cv2.drawContours(image, [approx], -1, (0, 255, 0), 2)
        else:
            box = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(box)
            box = np.array(box, dtype="int")
            box = perspective.order_points(box)
            cv2.drawContours(image, [box.astype("int")], -1, (0, 255, 0), 2)

        # Calculate area
        area_in_m2 = calculate_area(shape, cnt, pixel_per_m)

        # Print area for debugging
        area_in_pixels = cv2.contourArea(cnt)
        print(f"Shape: {shape}")
        print(f"Area in Pixels: {area_in_pixels}")
        print(f"Area in m²: {area_in_m2}")
        print(f"Pixel per Meter: {pixel_per_m}\n")

        # Draw area and color information
        if shape == "circle":
            center_x, center_y = int(x), int(y)
        else:
            tl, tr, br, bl = box
            center_x = int((tl[0] + tr[0] + br[0] + bl[0]) / 4)
            center_y = int((tl[1] + tr[1] + br[1] + bl[1]) / 4)

        cv2.putText(image, "{:.4f}m^2".format(area_in_m2), (center_x - 15, center_y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

        b, g, r = image[center_y, center_x]
        color_name = get_color(r, g, b, csv)
        cv2.putText(image, f"{color_name} ({shape})", (center_x, center_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Show the image with the drawn contours and text
    show_images([image])
