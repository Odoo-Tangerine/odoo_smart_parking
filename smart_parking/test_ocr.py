import easyocr
import os
import cv2
reader = easyocr.Reader(['en'])

for img in os.listdir('test_ocr'):
    frame = cv2.imread(f'./test_ocr/{img}')
    brighter_image = cv2.convertScaleAbs(frame, alpha=1.2, beta=0)
    license_plate_cropped_gray = cv2.cvtColor(brighter_image, cv2.COLOR_BGR2GRAY)
    imgBlurred = cv2.GaussianBlur(license_plate_cropped_gray, (5, 5), 0)

    _, license_plate_cropped_threshold = cv2.threshold(license_plate_cropped_gray,
                                                       64, 255, cv2.THRESH_BINARY_INV)
    results = reader.readtext(license_plate_cropped_threshold)
    print(results)

