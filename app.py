from flask import Flask, render_template, url_for, request, jsonify
import os
from werkzeug.utils import secure_filename
from change_detection import process_image
import google.generativeai as genai
import json
from geopy.distance import geodesic
from collections import defaultdict
import re

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

# Configure Gemini API
try:
    genai.configure(api_key="AIzaSyBdsP5kfGJb2DkqN7Ax4A2hwP9_ZaIn2c4")  # Using the new API key
    print("✅ Successfully configured Gemini API")
    
    # Test the API configuration
    test_model = genai.GenerativeModel('gemini-1.5-pro-latest')
    test_response = test_model.generate_content("Test message")
    print("✅ Successfully tested Gemini API connection")
except Exception as e:
    print(f"❌ Error configuring Gemini API: {str(e)}")
    raise

# Load GeoJSON data for 6th of October
try:
    with open(os.path.join('static', 'data', '6_october.geojson'), "r", encoding="utf-8") as file:
        october_data = json.load(file)
    print("✅ Successfully loaded 6th of October data")
except Exception as e:
    print(f"❌ Error loading 6th of October data: {str(e)}")
    october_data = {"features": []}

# Load GeoJSON data for 10th of Ramadan
try:
    with open('10_of_ramdan_restored2.geojson', "r", encoding="utf-8") as file:
        ramadan_data = json.load(file)
    print("✅ Successfully loaded 10th of Ramadan data")
except Exception as e:
    print(f"❌ Error loading 10th of Ramadan data: {str(e)}")
    ramadan_data = {"features": []}

# Set of basic services
all_possible_services = {"hospital", "mall", "parking", "fuel", "supermarket", "pharmacy", "bank", "school"}
# ✅ مجموعة الخدمات الأساسية اللي هنشتغل عليها
all_possible_services = {"hospital", "mall", "parking", "fuel", "supermarket", "pharmacy", "bank", "school"}

# ✅ إعداد نموذج Gemini
generation_config = {
    "temperature": 0.8,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

system_instruction = """
أنت مساعد ذكي تم تدريبه خصيصًا لتقديم معلومات دقيقة وموثوقة عن مدينة السادس من أكتوبر في مصر. لديك قاعدة بيانات تحتوي على مواقع جميع الخدمات المتوفرة في المدينة مثل المستشفيات، الصيدليات، المولات، مواقف السيارات، المدارس، البنوك، محطات الوقود، وغيرها، مع تفاصيل دقيقة تشمل الاسم، العنوان، نوع الخدمة، وخط العرض والطول لكل موقع.

✅ مهامك:
1. الرد على استفسارات المستخدمين بدقة وسرعة، دون مطالبتهم بمعلومات إضافية مثل الإحداثيات أو تحديدات دقيقة.
2. إذا سأل المستخدم عن منطقة معينة، استخدم أقرب بيانات متوفرة في قاعدة بياناتك لتقدير النتائج، حتى لو لم تكن تملك تقسيمًا دقيقًا للمدينة. لا تخبر المستخدم بعدم توفر بيانات، بل اعرض عليه أقرب النتائج الممكنة بناءً على المعلومات المتوفرة لديك.
3. اقتراح الخدمات الناقصة في منطقة بناءً على المقارنة بين الخدمات الموجودة والخدمات المفترض توافرها.
4. إعطاء توصيات دقيقة، كما لو كنت نظام توصية (Recommender System).
5. تقديم معلومات عامة عن المدينة أو أحيائها إذا طُلب منك.
6. الردود يجب أن تكون باللغة العربية وبأسلوب بسيط وواضح.

📍 تعامل مع كل استعلام بدقة، ولا تفترض أي معلومة غير موجودة في البيانات.
📍 إذا لم تتوفر بيانات كافية عن منطقة معينة، وضّح ذلك للمستخدم.
- الإجابة بدقة على أي استفسار يتعلق بالخدمات في المدينة.
- تقديم توصيات واقتراحات مدروسة بناءً على البيانات المتاحة.
- توضيح المناطق التي تحتوي على خدمات متنوعة أو تفتقر لخدمات معينة.
- عدم شرح العمليات أو الحسابات التي قمت بها – فقط أعطِ النتيجة مباشرة.

❌ لا تذكر أنك "ستقوم بالتحليل" أو أنك "بحاجة للمزيد من الوقت".
✅ فقط أعطِ الإجابة النهائية باحترافية وبأسلوب واثق وموضوعي.

📌 إذا طُلب منك تحليل شامل، أظهر أهم المناطق الغنية بالخدمات وتلك التي تفتقر إليها، مع اقتراح مناطق للاستثمار.

◾ عندما تقترح أماكن أو خدمات:
- اعرض خدمات مختلفة من أماكن متعددة داخل المدينة، ولا تكرر نفس المكان (مثل "مول مصر" أو "سيتي سكيب") إلا إذا كان فعلاً هو الأقرب.
- استخرج مجموعة متنوعة من الأماكن بناء على بيانات خطوط الطول والعرض المتاحة لديك.
- غطِّ مناطق سكنية وتجارية مختلفة عند تقديم الاقتراحات، مثل الأحياء السكنية، المجاورات، أو الطرق الرئيسية.
- هدفك هو تقديم تجربة ثرية للمستخدم بدون تكرار أو تعميم زائد.

تأكد من:
- إعطاء إجابات مباشرة وواضحة.
- تقديم أسماء الخدمات المتوفرة (مثل أسماء المستشفيات، المطاعم، البنوك...).
- تقديم توصيات ذكية في حال عدم توفر خدمات في منطقة معينة.
- استخدام بيانات خطوط الطول والعرض داخليًا فقط لتحسين الدقة، دون سؤال المستخدم عنها.

إذا سُئلت عن منطقة لا تعرفها، لا تقل "لا أملك معلومات"، بل ابحث في أقرب منطقة مشابهة وقدم إجابة مفيدة بناءً على ذلك.

استخدم المعلومات المتاحة لديك لتقديم أفضل إجابة ممكنة.
"""

# Configure Gemini models for each city
october_model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    system_instruction=system_instruction
)

ramadan_system_instruction = system_instruction.replace("السادس من أكتوبر", "العاشر من رمضان")
ramadan_model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    system_instruction=ramadan_system_instruction
)

# Initialize chat sessions
october_chat_session = october_model.start_chat(history=[])
ramadan_chat_session = ramadan_model.start_chat(history=[])

# ✅ دالة: استخراج الخدمات القريبة والمفقودة حول نقطة معينة
def get_services_near_location(lat, lon, radius_km=1.0, city_data=None):
    if city_data is None:
        city_data = october_data  # Default to 6th of October data
    
    location = (lat, lon)
    nearby_services = []
    all_services = set()

    for feature in city_data["features"]:
        props = feature["properties"]
        if "amenity" in props and "latitude" in props and "longitude" in props:
            service_location = (props["latitude"], props["longitude"])
            distance = geodesic(location, service_location).km
            if distance <= radius_km:
                nearby_services.append({
                    "name": props.get("name_ar", props.get("name_en", "بدون اسم")),
                    "type": props["amenity"],
                    "distance_km": round(distance, 2),
                    "lat": props["latitude"],
                    "lon": props["longitude"]
                })
                all_services.add(props["amenity"])

    missing_here = all_possible_services - all_services
    return nearby_services, missing_here

# ✅ دالة: توصيات بالخدمات الناقصة في كل منطقة
def recommend_services_by_area(city_data=None):
    if city_data is None:
        city_data = october_data  # Default to 6th of October data
    
    area_services = defaultdict(set)
    area_coords = defaultdict(list)

    for feature in city_data["features"]:
        props = feature["properties"]
        city = props.get("address_city", "غير معروف")
        street = props.get("address_street", "غير معروف")
        area_key = f"{city} - {street}"

        if "amenity" in props:
            area_services[area_key].add(props["amenity"])
        if "latitude" in props and "longitude" in props:
            area_coords[area_key].append((props["latitude"], props["longitude"]))

    recommendations = []

    for area, services in area_services.items():
        missing = all_possible_services - services
        coords = area_coords[area]

        if missing and coords:  # ✅ نتحقق إن في إحداثيات
            lat = round(sum([c[0] for c in coords]) / len(coords), 6)
            lon = round(sum([c[1] for c in coords]) / len(coords), 6)
            recommendations.append({
                "area": area,
                "missing_services": list(missing),
                "suggested_location": (lat, lon)
            })

    return recommendations


# ✅ دالة: تحليل شامل للمدينة وتحديد أماكن تحتاج استثمار
def full_city_analysis(city_data=None, city_name="السادس من أكتوبر"):
    if city_data is None:
        city_data = october_data  # Default to 6th of October data
    
    recs = recommend_services_by_area(city_data)
    if not recs:
        return "✅ كل المناطق تحتوي على الخدمات الأساسية المطلوبة."

    result = f"🏙️ تحليل شامل لمدينة {city_name}:\n\n"
    for rec in recs:
        result += f"📍 المنطقة: {rec['area']}\n"
        result += f"- الخدمات الناقصة: {', '.join(rec['missing_services'])}\n"
        result += f"- إحداثيات مقترحة: {rec['suggested_location']}\n\n"

    return result

# ✅ الدالة الرئيسية: التعامل مع استفسارات المستخدم
def chat_with_gemini_6th_october(user_query):
    print(f"Processing 6th October query: {user_query}")
    try:
        # لو فيه إحداثيات في السؤال
        lat_lon_match = re.search(r"خط العرض\s*([\d.]+)\s*وخ(ط)? الطول\s*([\d.]+)", user_query)
        if lat_lon_match:
            lat = float(lat_lon_match.group(1))
            lon = float(lat_lon_match.group(3))
            services, missing = get_services_near_location(lat, lon, city_data=october_data)
            print(f"Found {len(services)} services near location")

            if not services:
                return f"🚫 لا توجد خدمات قريبة في دائرة نصف قطرها 1 كم من النقطة ({lat}, {lon})."

            reply = f"📍 الخدمات المتوفرة حول ({lat}, {lon}):\n"
            for s in services:
                reply += f"- {s['type']}: {s['name']} (يبعد {s['distance_km']} كم)\n"

            if missing:
                reply += "\n🚧 الخدمات الناقصة في هذه المنطقة:\n"
                for m in missing:
                    reply += f"- {m}\n"
            else:
                reply += "\n✅ كل الخدمات الأساسية متوفرة في هذه المنطقة."

            return reply

        # لو السؤال عن التحليل الشامل
        if "حلل المدينة" in user_query or "المناطق الناقصة" in user_query:
            return full_city_analysis(october_data, "السادس من أكتوبر")

        # أي استفسار تاني → نبعت لـ Gemini
        print("Sending query to Gemini (October)")
        october_chat_session.send_message(user_query)
        response = october_chat_session.last.text
        print(f"Received response from Gemini (October): {response[:100]}...")
        return response
    except Exception as e:
        print(f"❌ Error in chat_with_gemini_6th_october: {str(e)}")
        raise

def chat_with_gemini_10th_ramadan(user_query):
    print(f"Processing 10th Ramadan query: {user_query}")
    try:
        # لو فيه إحداثيات في السؤال
        lat_lon_match = re.search(r"خط العرض\s*([\d.]+)\s*وخ(ط)? الطول\s*([\d.]+)", user_query)
        if lat_lon_match:
            lat = float(lat_lon_match.group(1))
            lon = float(lat_lon_match.group(3))
            services, missing = get_services_near_location(lat, lon, city_data=ramadan_data)
            print(f"Found {len(services)} services near location")

            if not services:
                return f"🚫 لا توجد خدمات قريبة في دائرة نصف قطرها 1 كم من النقطة ({lat}, {lon})."

            reply = f"📍 الخدمات المتوفرة حول ({lat}, {lon}):\n"
            for s in services:
                reply += f"- {s['type']}: {s['name']} (يبعد {s['distance_km']} كم)\n"

            if missing:
                reply += "\n🚧 الخدمات الناقصة في هذه المنطقة:\n"
                for m in missing:
                    reply += f"- {m}\n"
            else:
                reply += "\n✅ كل الخدمات الأساسية متوفرة في هذه المنطقة."

            return reply

        # لو السؤال عن التحليل الشامل
        if "حلل المدينة" in user_query or "المناطق الناقصة" in user_query:
            return full_city_analysis(ramadan_data, "العاشر من رمضان")

        # أي استفسار تاني → نبعت لـ Gemini
        print("Sending query to Gemini (Ramadan)")
        ramadan_chat_session.send_message(user_query)
        response = ramadan_chat_session.last.text
        print(f"Received response from Gemini (Ramadan): {response[:100]}...")
        return response
    except Exception as e:
        print(f"❌ Error in chat_with_gemini_10th_ramadan: {str(e)}")
        raise

@app.route('/chat', methods=['POST'])
def chat():
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
            response = "مدينتي قيد التطوير. سيتم إضافة المساعد قريباً."
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

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True)


