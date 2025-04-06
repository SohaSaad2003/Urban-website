import cv2
import numpy as np
import os
from datetime import datetime

def calculate_changed_pixels(img1, img2):
    """Calculate the changed pixels between two images and return threshold map."""
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    gray1_blurred = cv2.GaussianBlur(gray1, (21, 21), 0)
    gray2_blurred = cv2.GaussianBlur(gray2, (21, 21), 0)

    diff = cv2.absdiff(gray1_blurred, gray2_blurred)
    _, thresh = cv2.threshold(diff, 15, 255, cv2.THRESH_BINARY)

    changed_area = cv2.countNonZero(thresh)
    return thresh, changed_area

def process_images(image1_path, image2_path):
    """Process two images and return paths to the result images."""
    try:
        # Read images
        img1 = cv2.imread(image1_path)
        img2 = cv2.imread(image2_path)

        if img1 is None or img2 is None:
            raise ValueError("Failed to load images")

        # Ensure images are the same size
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        # Get the black and white threshold map
        thresh, _ = calculate_changed_pixels(img1, img2)

        # Create first result image with red contours
        result1 = img1.copy()
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(result1, contours, -1, (0, 0, 255), 2)  # Red color (BGR format)

        # Convert threshold to 3-channel image for saving
        result2 = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

        # Generate unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result1_path = os.path.join('static/results', f'change_map1_{timestamp}.jpg')
        result2_path = os.path.join('static/results', f'change_map2_{timestamp}.jpg')

        # Save results
        cv2.imwrite(result1_path, result1)
        cv2.imwrite(result2_path, result2)

        return result1_path, result2_path

    except Exception as e:
        raise Exception(f"Error processing images: {str(e)}")
