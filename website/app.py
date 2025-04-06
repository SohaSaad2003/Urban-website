from flask import Flask, render_template, url_for, request, jsonify
import os
from werkzeug.utils import secure_filename
from change_detection import process_images

# إنشاء تطبيق Flask
app = Flask(__name__)

# Configure upload and results folders
UPLOAD_FOLDER = os.path.join('static', 'uploads')
RESULT_FOLDER = os.path.join('static', 'results')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Ensure directories are writable
try:
    test_file = os.path.join(UPLOAD_FOLDER, 'test.txt')
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
    
    test_file = os.path.join(RESULT_FOLDER, 'test.txt')
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
except Exception as e:
    print(f"Warning: Directory permission issue - {str(e)}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/process_images', methods=['POST'])
def handle_image_processing():
    try:
        # Check if both images were uploaded
        if 'image1' not in request.files or 'image2' not in request.files:
            return jsonify({'error': 'Please upload both images'}), 400

        image1 = request.files['image1']
        image2 = request.files['image2']

        # Validate files
        if image1.filename == '' or image2.filename == '':
            return jsonify({'error': 'No selected files'}), 400

        if not (allowed_file(image1.filename) and allowed_file(image2.filename)):
            return jsonify({'error': 'Invalid file format. Please use PNG or JPG'}), 400

        # Save uploaded files
        filename1 = secure_filename(image1.filename)
        filename2 = secure_filename(image2.filename)

        filepath1 = os.path.join(UPLOAD_FOLDER, filename1)
        filepath2 = os.path.join(UPLOAD_FOLDER, filename2)

        image1.save(filepath1)
        image2.save(filepath2)

        # Process images
        result_paths = process_images(filepath1, filepath2)

        # Return results
        return jsonify({
            'change_map1': url_for('static', filename=f'results/{os.path.basename(result_paths[0])}'),
            'change_map2': url_for('static', filename=f'results/{os.path.basename(result_paths[1])}')
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # Cleanup uploaded files
        try:
            if 'filepath1' in locals(): os.remove(filepath1)
            if 'filepath2' in locals(): os.remove(filepath2)
        except:
            pass

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    try:
        # Check if image was uploaded
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'Please upload an image'}), 400

        image = request.files['image']

        # Validate file
        if image.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'}), 400

        if not allowed_file(image.filename):
            return jsonify({'success': False, 'error': 'Invalid file format. Please use PNG or JPG'}), 400

        # Save uploaded file
        filename = secure_filename(image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)

        try:
            # Process the image using our analysis functions
            from analysis3 import process_and_analyze_image
            results = process_and_analyze_image(filepath)
            
            if not results['success']:
                return jsonify({'success': False, 'error': results['error']}), 500

            # Format URLs like the change detection page
            classification_path = f"/{results['classificationImage']}"
            ndvi_path = f"/{results['ndviImage']}"

            print(f"Debug - Generated URLs: {classification_path}, {ndvi_path}")  # Debug print

            response_data = {
                'success': True,
                'landChange': results['landChange'],
                'emptyLand': results['emptyLand'],
                'classificationImage': classification_path,
                'ndviImage': ndvi_path,
                'denseVeg': results['denseVeg'],
                'lowVeg': results['lowVeg'],
                'nonVeg': results['nonVeg']
            }

            print(f"Debug - Full response data: {response_data}")  # Debug print
            return jsonify(response_data)

        finally:
            # Cleanup uploaded file
            try:
                os.remove(filepath)
            except:
                pass

    except Exception as e:
        print(f"Error in analyze_image: {str(e)}")  # Debug print
        return jsonify({'success': False, 'error': str(e)}), 500

# إنشاء صفحة رئيسية
@app.route('/')
def home():
    return render_template('index.html')  # ربط الصفحة الرئيسية بملف HTML

@app.route('/about')
def about():
    team_members = [
        {
            'name': 'Amany Sarhan',
            'image': 'member1.jpg',
            'linkedin': 'https://www.linkedin.com/in/amany-sarhan-5b291b15/'
        },
        {
            'name': 'Maii Mohsen',
            'image': 'member2.jpg',
            'linkedin': 'https://www.linkedin.com/in/maii-mohsen-029105229/'
        },
        {
            'name': 'Mennah Khalid',
            'image': 'member3.jpg',
            'linkedin': 'http://www.linkedin.com/in/mennah-khalid'
        },
        {
            'name': 'Soha Saad',
            'image': 'member4.jpg',
            'linkedin': 'https://www.linkedin.com/in/soha-saad-58693a225/'
        },
        {
            'name': 'Mariam Haytham',
            'image': 'member5.jpg',
            'linkedin': 'https://www.linkedin.com/in/mariam-haytham-51363a163'
        },
        {
            'name': 'Mariam Haytham',
            'image': 'member6.jpg',
            'linkedin': 'https://www.linkedin.com/in/mariam-haytham-51363a163'
        }
    ]
    return render_template('about.html', team_members=team_members)

@app.route('/change-detection')
def change_detection():
    return render_template('change_detection.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/map')
def map():
    return render_template('index.html')

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True)


