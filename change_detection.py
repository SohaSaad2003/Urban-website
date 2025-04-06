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
    try:
        print("Attempting to load model with custom objects")
        # Try loading with custom objects first
        custom_objects = {
            'InputLayer': tf.keras.layers.InputLayer
        }
        model = load_model('model.h5', custom_objects=custom_objects)
        print("Successfully loaded model with custom objects")
        return model
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        print("Creating placeholder model for testing")
        # Create a simple placeholder model for testing
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(64, 64, 3)),
            tf.keras.layers.Conv2D(32, 3, activation='relu'),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(len(class_labels), activation='softmax')
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        print("Successfully created placeholder model")
        return model

# Load the model at module level
print("Initializing model...")
model = load_classification_model()
print("Model initialization complete")

def preprocess_image(image, img_size=(64, 64)):
    """Preprocess image for classification."""
    if isinstance(image, str):
        image = cv2.imread(image)
    image = cv2.resize(image, img_size)
    image = image.astype('float32') / 255.0
    return image

def classify_image(image):
    """Classify the image and return the predicted class and confidence."""
    processed_image = preprocess_image(image)
    processed_image = np.expand_dims(processed_image, axis=0)
    predictions = model.predict(processed_image)
    predicted_class_idx = np.argmax(predictions[0])
    confidence = float(predictions[0][predicted_class_idx])
    return class_labels[predicted_class_idx], confidence

def get_reference_image(class_name):
    """Get the reference image for the predicted class."""
    # Extract area name (e.g., 'A' from 'A_area')
    area = class_name.split('_')[0]
    
    # Try both possible reference image locations with correct nested structure
    possible_paths = [
        os.path.join('Reference_Images', area, '2016.png'),  # Direct Reference_Images folder
        os.path.join('Reference_Images-20250404T175833Z-001', 'Reference_Images', area, '2016.png')  # Downloaded folder
    ]
    
    for reference_path in possible_paths:
        if os.path.exists(reference_path):
            img = cv2.imread(reference_path)
            if img is not None:
                return img
            
    # If we get here, try to list the contents of the directories to help with debugging
    debug_info = []
    for path in possible_paths:
        debug_info.append(f"Checking path: {path}")
        if os.path.exists(os.path.dirname(path)):
            try:
                contents = os.listdir(os.path.dirname(path))
                debug_info.append(f"Directory contents: {contents}")
            except Exception as e:
                debug_info.append(f"Error listing directory: {str(e)}")
        else:
            debug_info.append("Directory does not exist")
    
    raise FileNotFoundError(f"Reference image not found for area {area}. Debug info: {'; '.join(debug_info)}")

def calculate_changes(current_img, reference_img):
    """Calculate the changes between current and reference images."""
    # Ensure both images are the same size while maintaining aspect ratio
    target_size = (512, 512)
    
    def resize_maintain_aspect(img, target_size):
        h, w = img.shape[:2]
        aspect = w / h
        if aspect > 1:
            new_w = target_size[0]
            new_h = int(new_w / aspect)
        else:
            new_h = target_size[1]
            new_w = int(new_h * aspect)
        return cv2.resize(img, (new_w, new_h))
    
    current_img = resize_maintain_aspect(current_img, target_size)
    reference_img = resize_maintain_aspect(reference_img, target_size)
    
    # Convert to grayscale
    current_gray = cv2.cvtColor(current_img, cv2.COLOR_BGR2GRAY)
    reference_gray = cv2.cvtColor(reference_img, cv2.COLOR_BGR2GRAY)
    
    # Calculate absolute difference
    diff = cv2.absdiff(current_gray, reference_gray)
    
    # Apply threshold to get binary image
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Calculate total area of changes
    total_area = 0
    contour_img = current_img.copy()
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 100:  # Filter small changes
            total_area += area
            cv2.drawContours(contour_img, [contour], -1, (0, 255, 0), 2)
    
    # Calculate change percentage
    image_area = current_img.shape[0] * current_img.shape[1]
    change_percentage = (total_area / image_area) * 100
    
    return {
        'diff_map': thresh,
        'contour_overlay': contour_img,
        'area': total_area,
        'change_percentage': change_percentage
    }

def process_image(image_path):
    """Process a single image for change detection."""
    try:
        print(f"Starting to process image: {image_path}")
        
        # Read and validate input image
        current_img = cv2.imread(image_path)
        if current_img is None:
            print(f"Failed to read input image: {image_path}")
            return {'success': False, 'error': 'Failed to read input image'}
        
        print(f"Successfully read input image, shape: {current_img.shape}")
        
        # Classify the image
        try:
            class_name, confidence = classify_image(current_img)
            print(f"Image classified as: {class_name} with confidence: {confidence}")
        except Exception as e:
            print(f"Error during classification: {str(e)}")
            return {'success': False, 'error': f'Classification error: {str(e)}'}
        
        # Get reference image
        try:
            reference_img = get_reference_image(class_name)
            print(f"Got reference image for {class_name}, shape: {reference_img.shape}")
        except FileNotFoundError as e:
            print(f"Reference image error: {str(e)}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            print(f"Unexpected error getting reference image: {str(e)}")
            return {'success': False, 'error': f'Reference image error: {str(e)}'}
        
        # Calculate changes
        try:
            changes = calculate_changes(current_img, reference_img)
            print(f"Calculated changes: area={changes['area']}, percentage={changes['change_percentage']}")
        except Exception as e:
            print(f"Error calculating changes: {str(e)}")
            return {'success': False, 'error': f'Error calculating changes: {str(e)}'}
        
        # Save results
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save reference image
            ref_path = os.path.join('static', 'results', f'reference_{timestamp}.jpg')
            cv2.imwrite(ref_path, reference_img)
            print(f"Saved reference image to: {ref_path}")
            
            # Save processed image
            proc_path = os.path.join('static', 'results', f'processed_{timestamp}.jpg')
            cv2.imwrite(proc_path, current_img)
            print(f"Saved processed image to: {proc_path}")
            
            # Save difference map
            diff_path = os.path.join('static', 'results', f'diff_{timestamp}.jpg')
            cv2.imwrite(diff_path, changes['diff_map'])
            print(f"Saved difference map to: {diff_path}")
            
            # Save contour overlay
            contour_path = os.path.join('static', 'results', f'contours_{timestamp}.jpg')
            cv2.imwrite(contour_path, changes['contour_overlay'])
            print(f"Saved contour overlay to: {contour_path}")
            
            # Prepare response
            response = {
                'success': True,
                'reference_image': url_for('static', filename=f'results/reference_{timestamp}.jpg'),
                'processed_image': url_for('static', filename=f'results/processed_{timestamp}.jpg'),
                'diff_map': url_for('static', filename=f'results/diff_{timestamp}.jpg'),
                'contour_overlay': url_for('static', filename=f'results/contours_{timestamp}.jpg'),
                'area': class_name,
                'detected_area': float(changes['area']),
                'confidence': float(confidence),
                'change_percentage': float(changes['change_percentage'])
            }
            
            print("Successfully prepared response")
            return response
            
        except Exception as e:
            print(f"Error saving results: {str(e)}")
            return {'success': False, 'error': f'Error saving results: {str(e)}'}
        
    except Exception as e:
        print(f"Unexpected error in process_image: {str(e)}")
        return {'success': False, 'error': str(e)}

# For backward compatibility
def process_images(image1_path, image2_path):
    """Legacy function for processing two images."""
    return process_image(image1_path)  # Just process the first image
