import cv2
import numpy as np
import os
from datetime import datetime
import tensorflow as tf
from keras.models import load_model
from flask import url_for

# Classification labels
class_labels = ['A_area', 'B_area', 'C_area', 'D_area', 'E_area', 'F_area',
                'G_area', 'H_area', 'I_area', 'J_area', 'K_area', 'L_area',
                'M_area', 'N_area', 'O_area']

def load_classification_model():
    model_path = os.path.join(os.path.dirname(__file__), 'model.h5')
    print(f"Trying to load model from: {model_path}")
    
    try:
        model = load_model(model_path, compile=False)
        print("Successfully loaded model")
        return model
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        print("Creating placeholder model for testing")
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(64, 64, 3)),
            tf.keras.layers.Conv2D(32, 3, activation='relu'),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(len(class_labels), activation='softmax')
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        print("Successfully created placeholder model")
        return model

# Load model globally
print("Initializing model...")
model = load_classification_model()
print("Model initialization complete")

def preprocess_image(image, img_size=(64, 64)):
    if isinstance(image, str):
        image = cv2.imread(image)
        if image is None:
            raise ValueError("Could not read image file")
    
    # Convert to RGB if image is in BGR format
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Resize image
    image = cv2.resize(image, img_size, interpolation=cv2.INTER_AREA)
    
    # Normalize pixel values
    image = image.astype('float32')
    
    # Apply histogram equalization for better contrast
    if len(image.shape) == 3:
        lab = cv2.cvtColor(image.astype('uint8'), cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl,a,b))
        image = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    
    # Normalize to [0,1] range
    image = image / 255.0
    
    return image

def classify_image(image):
    try:
        processed_image = preprocess_image(image)
        processed_image = np.expand_dims(processed_image, axis=0)
        
        # Get predictions
        predictions = model.predict(processed_image, verbose=0)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        
        # Get top 3 predictions for better insight
        top_3_idx = np.argsort(predictions[0])[-3:][::-1]
        top_3_predictions = [(class_labels[idx], float(predictions[0][idx])) for idx in top_3_idx]
        
        print(f"Top 3 predictions: {top_3_predictions}")
        
        return class_labels[predicted_class_idx], confidence
    except Exception as e:
        print(f"Error in classification: {str(e)}")
        return None, 0.0

def get_reference_image(class_name):
    area = class_name.split('_')[0]
    possible_paths = [
        os.path.join('Reference_Images', area, '2016.png'),
        os.path.join('Reference_Images-20250404T175833Z-001', 'Reference_Images', area, '2016.png')
    ]
    for reference_path in possible_paths:
        if os.path.exists(reference_path):
            img = cv2.imread(reference_path)
            if img is not None:
                return img
    raise FileNotFoundError(f"Reference image not found for area {area}")

def calculate_changes(current_img, reference_img):
    target_size = (512, 512)

    def resize_fixed(img, size=(512, 512)):
        return cv2.resize(img, size, interpolation=cv2.INTER_AREA)

    # Resize both images to the same fixed size
    current_img = resize_fixed(current_img, target_size)
    reference_img = resize_fixed(reference_img, target_size)

    # Apply slight blur to reduce noise impact
    current_blur = cv2.GaussianBlur(current_img, (5, 5), 0)
    reference_blur = cv2.GaussianBlur(reference_img, (5, 5), 0)

    # Use RGB difference instead of grayscale
    diff = cv2.absdiff(current_blur, reference_blur)

    # Convert diff to grayscale for thresholding
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    # Threshold to isolate strong differences
    _, thresh = cv2.threshold(diff_gray, 15, 255, cv2.THRESH_BINARY)

    # Find contours in the thresholded diff image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    total_area = 0
    contour_img = current_img.copy()

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 30:  # Ignore tiny changes
            total_area += area
            cv2.drawContours(contour_img, [contour], -1, (0, 255, 0), 2)  # Green color

    # Calculate change percentage based on pixel count
    image_area = current_img.shape[0] * current_img.shape[1]
    non_zero_pixels = cv2.countNonZero(thresh)
    change_percentage = (non_zero_pixels / image_area) * 100

    return {
        'diff_map': thresh,
        'contour_overlay': contour_img,
        'area': total_area,
        'change_percentage': change_percentage
    }

def process_image(image_path):
    try:
        print(f"Starting to process image: {image_path}")
        current_img = cv2.imread(image_path)
        if current_img is None:
            return {'success': False, 'error': 'Failed to read input image'}
        
        class_name, confidence = classify_image(current_img)
        reference_img = get_reference_image(class_name)
        changes = calculate_changes(current_img, reference_img)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_dir = os.path.join('static', 'results')
        os.makedirs(result_dir, exist_ok=True)

        ref_path = os.path.join(result_dir, f'reference_{timestamp}.jpg')
        proc_path = os.path.join(result_dir, f'processed_{timestamp}.jpg')
        diff_path = os.path.join(result_dir, f'diff_{timestamp}.jpg')
        contour_path = os.path.join(result_dir, f'contours_{timestamp}.jpg')

        cv2.imwrite(ref_path, reference_img)
        cv2.imwrite(proc_path, current_img)
        cv2.imwrite(diff_path, changes['diff_map'])
        cv2.imwrite(contour_path, changes['contour_overlay'])

        return {
            'success': True,
            'reference_image': url_for('static', filename=f'results/reference_{timestamp}.jpg'),
            'processed_image': url_for('static', filename=f'results/processed_{timestamp}.jpg'),
            'diff_map': url_for('static', filename=f'results/diff_{timestamp}.jpg'),
            'contour_overlay': url_for('static', filename=f'results/contours_{timestamp}.jpg'),
            'area': class_name,
            'detected_area': float(changes['area']),
            'confidence': float(confidence),
            'change_percentage': float(changes['change_percentage']),
            'alert': changes['change_percentage'] > 20.0,  # 💥 لو التغيير فوق 20%
            'alert_message': "⚠️ Warning: Suspicious changes detected in the area!" if changes['change_percentage'] > 20.0 else ""
        }

    except Exception as e:
        return {'success': False, 'error': f'Unexpected error: {str(e)}'}

# Backward compatibility
def process_images(image1_path, image2_path):
    return process_image(image1_path)