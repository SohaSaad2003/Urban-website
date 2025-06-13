from flask import Flask, render_template, url_for, request, jsonify
import os
from werkzeug.utils import secure_filename
from change_detection import process_image
from chat import chat_with_gemini_6th_october, chat_with_gemini_10th_ramadan, chat_with_gemini_madinaty
from image_caption import generate_caption_with_display

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

@app.route('/process_image', methods=['POST'])
def handle_image_processing():
    try:
        print("Starting image processing request")
        # Check if image was uploaded
        if 'image' not in request.files:
            print("No image file in request")
            return jsonify({'success': False, 'error': 'Please upload an image'}), 400

        image = request.files['image']

        # Validate file
        if image.filename == '':
            print("Empty filename")
            return jsonify({'success': False, 'error': 'No selected file'}), 400

        if not allowed_file(image.filename):
            print(f"Invalid file format: {image.filename}")
            return jsonify({'success': False, 'error': 'Invalid file format. Please use PNG or JPG'}), 400

        # Save uploaded file
        filename = secure_filename(image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Saving uploaded file to: {filepath}")
        image.save(filepath)

        try:
            # Process the image using our updated change detection
            print("Calling process_image function")
            results = process_image(filepath)
            
            if not results['success']:
                print(f"Processing failed: {results.get('error', 'Unknown error')}")
                return jsonify(results), 500

            print("Processing successful, returning results")
            return jsonify(results)

        finally:
            # Cleanup uploaded file
            try:
                os.remove(filepath)
                print(f"Cleaned up uploaded file: {filepath}")
            except Exception as e:
                print(f"Error cleaning up file: {str(e)}")

    except Exception as e:
        print(f"Unexpected error in handle_image_processing: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

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

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/chat_page')
def chat_page():
    return render_template('chat.html')

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

@app.route('/chat', methods=['POST'])
def chat_api():
    try:
        data = request.get_json()
        message = data.get('message')
        city = data.get('city')

        print(f"Received chat request - City: {city}, Message: {message}")

        if not message or not city:
            print("❌ Missing message or city parameter")
            return jsonify({'error': 'Missing message or city parameter'}), 400

        if city == 'october':
            print("Processing October request")
            response = chat_with_gemini_6th_october(message)
        elif city == 'madinaty':
            print("Processing Madinaty request")
            response = chat_with_gemini_madinaty(message)
        elif city == 'ramadan':
            print("Processing Ramadan request")
            response = chat_with_gemini_10th_ramadan(message)
        else:
            print(f"❌ Invalid city parameter: {city}")
            return jsonify({'error': 'Invalid city parameter'}), 400

        print(f"Sending response: {response[:100]}...")
        return jsonify({'response': response})
    except Exception as e:
        print(f"❌ Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/image_caption')
def image_caption():
    return render_template('image_caption.html')

@app.route('/generate_caption', methods=['POST'])
def generate_caption():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image = request.files['image']
        if image.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if not allowed_file(image.filename):
            return jsonify({'error': 'Invalid file format. Please use PNG or JPG'}), 400

        # Save uploaded file
        filename = secure_filename(image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)

        try:
            # Generate caption using the imported function
            caption = generate_caption_with_display(filepath)
            
            if caption is None:
                return jsonify({'error': 'Failed to generate caption'}), 500

            return jsonify({'caption': caption})

        finally:
            # Cleanup uploaded file
            try:
                os.remove(filepath)
            except:
                pass

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True)


