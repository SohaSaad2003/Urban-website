def classify_regions_and_generate_ndvi(image_path):
    """
    Classify regions in an image and generate NDVI map.
    Returns paths to generated images and analysis results.
    """
    try:
        # Load the image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Failed to load image.")

        # Convert the image to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Step 1: Classify regions using KMeans
        pixel_values = img_rgb.reshape((-1, 3))
        pixel_values = np.float32(pixel_values)

        # Apply KMeans clustering with 2 clusters
        kmeans = KMeans(n_clusters=2, random_state=0)
        kmeans.fit(pixel_values)

        # Reshape the clustered labels back to the original image shape
        segmented_image = kmeans.labels_.reshape(img.shape[:2])

        # Calculate percentages for land change and empty land
        total_pixels = segmented_image.size
        urban_pixels = np.count_nonzero(segmented_image == 0)  # Class 0: Buildings
        empty_pixels = np.count_nonzero(segmented_image == 1)  # Class 1: Empty areas

        urban_percentage = (urban_pixels / total_pixels) * 100
        empty_percentage = (empty_pixels / total_pixels) * 100

        print(f"Debug - Pixel counts: Urban={urban_pixels}, Empty={empty_pixels}, Total={total_pixels}")
        print(f"Debug - Percentages: Urban={urban_percentage:.2f}%, Empty={empty_percentage:.2f}%")

        # Generate timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create filenames with forward slashes
        classified_filename = f'classified_regions_{timestamp}.jpg'
        ndvi_filename = f'ndvi_map_{timestamp}.jpg'
        
        # Create relative paths (these will be returned to the frontend)
        classified_relative_path = 'static/results/' + classified_filename
        ndvi_relative_path = 'static/results/' + ndvi_filename
        
        # Create full paths for saving files
        results_dir = os.path.join(current_app.root_path, 'static', 'results')
        full_classified_path = os.path.join(results_dir, classified_filename)
        full_ndvi_path = os.path.join(results_dir, ndvi_filename)
        
        # Ensure directory exists
        os.makedirs(results_dir, exist_ok=True)
        
        # Create visualization of segmented image
        vis_image = np.zeros_like(img_rgb)
        vis_image[segmented_image == 0] = [64, 64, 64]     # Dark gray for urban
        vis_image[segmented_image == 1] = [210, 180, 140]  # Tan for empty
        
        # Save classification image
        plt.figure(figsize=(10, 8))
        plt.imshow(vis_image)
        plt.title('Land Classification')
        plt.axis('off')
        plt.savefig(full_classified_path, dpi=300, bbox_inches='tight', pad_inches=0)
        plt.close()

        # Calculate and save NDVI map
        red_channel = img_rgb[:, :, 0].astype(float)
        nir_channel = img_rgb[:, :, 2].astype(float)  # Assuming NIR is in the blue channel
        ndvi = (nir_channel - red_channel) / (nir_channel + red_channel + 1e-5)
        
        plt.figure(figsize=(10, 8))
        plt.imshow(ndvi, cmap='RdYlGn')
        plt.title('NDVI Analysis')
        plt.colorbar(label='NDVI')
        plt.axis('off')
        plt.savefig(full_ndvi_path, dpi=300, bbox_inches='tight', pad_inches=0)
        plt.close()

        # Calculate vegetation percentages from NDVI
        high_vegetation = np.sum(ndvi > 0.5) / total_pixels * 100
        low_vegetation = np.sum((ndvi > 0.2) & (ndvi <= 0.5)) / total_pixels * 100
        no_vegetation = np.sum(ndvi <= 0.2) / total_pixels * 100

        return {
            'success': True,
            'classified_image': classified_relative_path,
            'ndvi_map': ndvi_relative_path,
            'land_change': round(urban_percentage, 2),
            'empty_land': round(empty_percentage, 2),
            'vegetation_analysis': {
                'dense_vegetation': round(high_vegetation, 2),
                'low_vegetation': round(low_vegetation, 2),
                'non_vegetation': round(no_vegetation, 2)
            }
        }

    except Exception as e:
        print(f"Error in classify_regions_and_generate_ndvi: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def process_and_analyze_image(image_path):
    """
    Process an image and return analysis results.
    This function is designed to be called from Flask routes.
    """
    try:
        # Ensure the results directory exists
        results_dir = os.path.join(current_app.root_path, 'static', 'results')
        os.makedirs(results_dir, exist_ok=True)

        # Process the image and get results
        results = classify_regions_and_generate_ndvi(image_path)
        
        if not results['success']:
            return {
                'success': False,
                'error': results['error']
            }

        # Return processed results with correct paths for frontend
        return {
            'success': True,
            'landChange': results['land_change'],
            'emptyLand': results['empty_land'],
            'classificationImage': results['classified_image'],
            'ndviImage': results['ndvi_map'],
            'denseVeg': results['vegetation_analysis']['dense_vegetation'],
            'lowVeg': results['vegetation_analysis']['low_vegetation'],
            'nonVeg': results['vegetation_analysis']['non_vegetation']
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        } 