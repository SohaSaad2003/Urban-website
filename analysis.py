import cv2
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import os
from datetime import datetime

def classify_regions_and_generate_ndvi(image_path, k=2):
    """
    Classify regions in an image and generate NDVI map.
    Applies KMeans clustering followed by NDVI calculation.
    """
    try:
        # Load the image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Failed to load image.")

        # Convert the image to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Step 1: Classify regions using KMeans
        # Reshape the image to a 2D array of pixels
        pixel_values = img_rgb.reshape((-1, 3))
        pixel_values = np.float32(pixel_values)

        # Apply KMeans clustering
        kmeans = KMeans(n_clusters=k, random_state=0)
        kmeans.fit(pixel_values)

        # Reshape the clustered labels back to the original image shape
        segmented_image = kmeans.labels_.reshape(img.shape[:2])

        # Save the classified regions image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        classified_image_path = os.path.join(
            'static/results', f'classified_regions_{timestamp}.jpg'
        )
        plt.imshow(segmented_image, cmap='viridis')
        plt.axis('off')
        plt.savefig(classified_image_path, dpi=300)
        plt.close()

        # Step 2: Generate NDVI map
        # Extract Red and NIR channels
        red_channel = img_rgb[:, :, 0].astype(float)
        nir_channel = img_rgb[:, :, 2].astype(float)  # Assuming NIR is in the blue channel

        # Calculate NDVI
        ndvi = (nir_channel - red_channel) / (nir_channel + red_channel + 1e-5)

        # Save the NDVI map
        ndvi_map_path = os.path.join(
            'static/results', f'ndvi_map_{timestamp}.jpg'
        )
        plt.imshow(ndvi, cmap='RdYlGn')
        plt.colorbar(label='NDVI')
        plt.axis('off')
        plt.savefig(ndvi_map_path, dpi=300)
        plt.close()

        # Analyze NDVI percentages
        total_pixels = ndvi.size
        high_vegetation = np.sum(ndvi > 0.5) / total_pixels * 100
        low_vegetation = np.sum((ndvi > 0.2) & (ndvi <= 0.5)) / total_pixels * 100
        no_vegetation = np.sum(ndvi <= 0.2) / total_pixels * 100

        return {
            'classified_image_path': classified_image_path,
            'ndvi_map_path': ndvi_map_path,
            'ndvi_analysis': {
                'dense_vegetation': high_vegetation,
                'low_vegetation': low_vegetation,
                'non_vegetation': no_vegetation
            }
        }

    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")