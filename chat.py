import os
import json
import re
from collections import defaultdict
from geopy.distance import geodesic
import google.generativeai as genai

# Configure Gemini API
try:
    genai.configure(api_key="AIzaSyBdsP5kfGJb2DkqN7Ax4A2hwP9_ZaIn2c4")  # Using the new API key
    print("✅ Successfully configured Gemini API")
    
    # Test the API configuration
    test_model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
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
    with open(os.path.join('static', 'data', '10_of_ramdan_restored2.geojson'), "r", encoding="utf-8") as file:
        ramadan_data = json.load(file)
    print("✅ Successfully loaded 10th of Ramadan data")
except Exception as e:
    print(f"❌ Error loading 10th of Ramadan data: {str(e)}")
    ramadan_data = {"features": []}

# Load GeoJSON data for Madinaty
try:
    with open(os.path.join('static', 'data', 'madinaty.geojson'), "r", encoding="utf-8") as file:
        madinaty_data = json.load(file)
    print("✅ Successfully loaded Madinaty data")
except Exception as e:
    print(f"❌ Error loading Madinaty data: {str(e)}")
    madinaty_data = {"features": []}

# Set of basic services
all_possible_services = {"hospital", "mall", "parking", "fuel", "supermarket", "pharmacy", "bank", "school"}

# Configure Gemini models for each city
generation_config = {
    "temperature": 0.8,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

october_system_instruction = """
أنت مساعد ذكي تم تدريبه خصيصًا لتقديم معلومات دقيقة وموثوقة عن مدينة السادس من أكتوبر في مصر. لديك قاعدة بيانات تحتوي على مواقع جميع الخدمات المتوفرة في المدينة مثل المستشفيات، الصيدليات، المولات، مواقف السيارات، المدارس، البنوك، محطات الوقود، وغيرها، مع تفاصيل دقيقة تشمل الاسم، العنوان، نوع الخدمة، وخط العرض والطول لكل موقع.

✅ مهامك:
1. الرد على استفسارات المستخدمين بدقة وسرعة، دون مطالبتهم بمعلومات إضافية مثل الإحداثيات أو تحديدات دقيقة.
2. إذا سأل المستخدم عن منطقة معينة، استخدم أقرب بيانات متوفرة في قاعدة بياناتك لتقدير النتائج، حتى لو لم تكن تملك تقسيمًا دقيقًا للمدينة. لا تخبر المستخدم بعدم توفر بيانات، بل اعرض عليه أقرب النتائج الممكنة بناءً على المعلومات المتوفرة لديك.
3. اقتراح الخدمات الناقصة في منطقة بناءً على المقارنة بين الخدمات الموجودة والخدمات المفترض توافرها.
4. إعطاء توصيات دقيقة، كما لو كنت نظام توصية (Recommender System).
5. تقديم معلومات عامة عن المدينة أو أحيائها إذا طُلب منك.
6. الردود يجب أن تكون باللغة العربية وبأسلوب بسيط وواضح، مع تجنب الردود الطويلة جدًا، وتقديم الإجابة المطلوبة مباشرة مع ذكر اسم الخدمة أو المكان بشكل واضح وصريح.

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

ramadan_system_instruction = """
أنت مساعد ذكي تم تدريبه خصيصًا لتقديم معلومات دقيقة وموثوقة عن مدينة العاشر من رمضان في مصر. لديك قاعدة بيانات تحتوي على مواقع جميع الخدمات المتوفرة في المدينة مثل المستشفيات، الصيدليات، المولات، مواقف السيارات، المدارس، البنوك، محطات الوقود، وغيرها، مع تفاصيل دقيقة تشمل الاسم، العنوان، نوع الخدمة، وخط العرض والطول لكل موقع.

✅ مهامك:
1. الرد على استفسارات المستخدمين بدقة وسرعة، دون مطالبتهم بمعلومات إضافية مثل الإحداثيات أو تحديدات دقيقة.
2. إذا سأل المستخدم عن منطقة معينة، استخدم أقرب بيانات متوفرة في قاعدة بياناتك لتقدير النتائج، حتى لو لم تكن تملك تقسيمًا دقيقًا للمدينة. لا تخبر المستخدم بعدم توفر بيانات، بل اعرض عليه أقرب النتائج الممكنة بناءً على المعلومات المتوفرة لديك.
3. اقتراح الخدمات الناقصة في منطقة بناءً على المقارنة بين الخدمات الموجودة والخدمات المفترض توافرها.
4. إعطاء توصيات دقيقة، كما لو كنت نظام توصية (Recommender System).
5. تقديم معلومات عامة عن المدينة أو أحيائها إذا طُلب منك.
6. الردود يجب أن تكون باللغة العربية وبأسلوب بسيط وواضح، مع تجنب الردود الطويلة جدًا، وتقديم الإجابة المطلوبة مباشرة مع ذكر اسم الخدمة أو المكان بشكل واضح وصريح.

📍 تعامل مع كل استعلام بدقة، ولا تفترض أي معلومة غير موجودة في البيانات.
📍 إذا لم تتوفر بيانات كافية عن منطقة معينة، وضّح ذلك للمستخدم مع تقديم أقرب نتائج منطقية.

- الإجابة بدقة على أي استفسار يتعلق بالخدمات في المدينة.
- تقديم توصيات واقتراحات مدروسة بناءً على البيانات المتاحة.
- توضيح المناطق التي تحتوي على خدمات متنوعة أو تفتقر لخدمات معينة.
- عدم شرح العمليات أو الحسابات التي قمت بها – فقط أعطِ النتيجة مباشرة.

❌ لا تذكر أنك "ستقوم بالتحليل" أو أنك "بحاجة للمزيد من الوقت".
✅ فقط أعطِ الإجابة النهائية باحترافية وبأسلوب واثق وموضوعي.

📌 إذا طُلب منك تحليل شامل، أظهر أهم المناطق الغنية بالخدمات وتلك التي تفتقر إليها، مع اقتراح مناطق للاستثمار.

◾ عندما تقترح أماكن أو خدمات:
- اعرض خدمات مختلفة من أماكن متعددة داخل المدينة، ولا تكرر نفس المكان (مثل "مول مصر" أو "سنتر المدينة") إلا إذا كان فعلاً هو الأقرب.
- استخرج مجموعة متنوعة من الأماكن بناء على بيانات خطوط الطول والعرض المتاحة لديك.
- غطِّ مناطق سكنية وتجارية مختلفة عند تقديم الاقتراحات، مثل الأحياء السكنية، المجاورات، أو الطرق الرئيسية.
- هدفك هو تقديم تجربة ثرية للمستخدم بدون تكرار أو تعميم زائد.

📌 المدن التي تشملها تغطيتك:
- العاشر من رمضان

تأكد من:
- إعطاء إجابات مباشرة وواضحة.
- تقديم أسماء الخدمات المتوفرة (مثل أسماء المستشفيات، المطاعم، البنوك...).
- تقديم توصيات ذكية في حال عدم توفر خدمات في منطقة معينة.
- استخدام بيانات خطوط الطول والعرض داخليًا فقط لتحسين الدقة، دون سؤال المستخدم عنها.

إذا سُئلت عن منطقة لا تعرفها، لا تقل "لا أملك معلومات"، بل ابحث في أقرب منطقة مشابهة وقدم إجابة مفيدة بناءً على ذلك.

استخدم المعلومات المتاحة لديك لتقديم أفضل إجابة ممكنة.
"""

madinaty_system_instruction = """
أنت مساعد ذكي تم تدريبه خصيصًا لتقديم معلومات دقيقة وموثوقة عن مدينة مدينتي في مصر. لديك قاعدة بيانات تحتوي على مواقع جميع الخدمات المتوفرة في المدينة مثل المستشفيات، الصيدليات، المولات، مواقف السيارات، المدارس، البنوك، محطات الوقود، وغيرها، مع تفاصيل دقيقة تشمل الاسم، نوع الخدمة، وخط العرض والطول لكل موقع.

✅ مهامك:
1. الرد على استفسارات المستخدمين بدقة وسرعة، دون مطالبتهم بإحداثيات.
2. إذا طُلب منك معلومات عن منطقة غير معروفة، استخدم أقرب نقطة متوفرة في البيانات وقدّم إجابة تقديرية ذكية.
3. اقتراح الخدمات الناقصة في المناطق استنادًا إلى المقارنة بين الموجود والمفترض.
4. تقديم توصيات مدروسة كما لو كنت نظام توصية.
5. توضيح أي مناطق تحتاج إلى استثمار في خدمات جديدة.
6. الردود تكون دائمًا باللغة العربية وبأسلوب بسيط وواضح.

📍 استخدم بيانات خطوط الطول والعرض داخليًا لتحسين الدقة فقط.
📍 لا تطلب من المستخدم إحداثيات.
📍 لا تقل "لا توجد بيانات"، بل قدّم أقرب نتيجة ممكنة.

❌ لا تشرح طريقة التحليل أو المعالجة.
✅ فقط أعطِ الإجابة بثقة ووضوح.

📌 في التحليل الشامل، أبرز المناطق الغنية بالخدمات وتلك التي تحتاج لتطوير، وقدم اقتراحات ذكية مبنية على بياناتك.

استخدم المعلومات المتاحة لديك لتقديم أفضل إجابة ممكنة.
"""

# Initialize models and chat sessions
october_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-preview-05-20",
    generation_config=generation_config,
    system_instruction=october_system_instruction
)

ramadan_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-preview-05-20",
    generation_config=generation_config,
    system_instruction=ramadan_system_instruction
)

madinaty_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-preview-05-20",
    generation_config=generation_config,
    system_instruction=madinaty_system_instruction
)

# Initialize chat sessions
october_chat_session = october_model.start_chat(history=[])
ramadan_chat_session = ramadan_model.start_chat(history=[])
madinaty_chat_session = madinaty_model.start_chat(history=[])

# ✅ دالة: استخراج الخدمات القريبة والمفقودة حول نقطة معينة
def get_services_near_location(lat, lon, radius_km=1.0, city_data=None):
    if city_data is None:
        city_data = october_data  # Default to 6th of October data
    
    location = (lat, lon)
    nearby_services = []
    all_services = set()
    area_info = None

    for feature in city_data["features"]:
        props = feature["properties"]
        if "amenity" in props and "latitude" in props and "longitude" in props:
            service_location = (props["latitude"], props["longitude"])
            distance = geodesic(location, service_location).km
            if distance <= radius_km:
                # Get area information if available
                if not area_info and "address_street" in props:
                    area_info = props.get("address_street", "غير معروف")
                
                nearby_services.append({
                    "name": props.get("name_ar", props.get("name_en", "بدون اسم")),
                    "type": props["amenity"],
                    "distance_km": round(distance, 2),
                    "lat": props["latitude"],
                    "lon": props["longitude"],
                    "address": props.get("address_street", "غير معروف")
                })
                all_services.add(props["amenity"])

    missing_here = all_possible_services - all_services
    return nearby_services, missing_here, area_info

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
        # Handle location-based queries
        lat_lon_match = re.search(r"خط العرض\s*([\d.]+)\s*وخ(ط)? الطول\s*([\d.]+)", user_query)
        if lat_lon_match:
            lat = float(lat_lon_match.group(1))
            lon = float(lat_lon_match.group(3))
            services, missing, area_info = get_services_near_location(lat, lon, city_data=october_data)
            return format_service_response(services, missing, area_info, "السادس من أكتوبر")

        # Handle city analysis queries
        if "حلل المدينة" in user_query or "المناطق الناقصة" in user_query:
            return full_city_analysis(october_data, "السادس من أكتوبر")

        # Handle general queries
        print("Sending query to Gemini (October)")
        october_chat_session.send_message(user_query)
        response = october_chat_session.last.text
        
        # Enhance the response with specific details
        if "لا يوجد" in response or "غير متوفر" in response:
            return "🔍 لم أجد المعلومات المطلوبة بالضبط، لكن دعني أقدم لك معلومات عن المناطق المجاورة في السادس من أكتوبر. هل يمكنك تحديد المنطقة التي تبحث عنها بشكل أدق؟"
        
        return response

    except Exception as e:
        print(f"❌ Error in chat_with_gemini_6th_october: {str(e)}")
        return "⚠️ عذراً، حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى أو تقديم المزيد من التفاصيل عن المنطقة التي تبحث عنها."

def chat_with_gemini_10th_ramadan(user_query):
    print(f"Processing 10th Ramadan query: {user_query}")
    try:
        # Handle location-based queries
        lat_lon_match = re.search(r"خط العرض\s*([\d.]+)\s*وخ(ط)? الطول\s*([\d.]+)", user_query)
        if lat_lon_match:
            lat = float(lat_lon_match.group(1))
            lon = float(lat_lon_match.group(3))
            services, missing, area_info = get_services_near_location(lat, lon, city_data=ramadan_data)
            return format_service_response(services, missing, area_info, "العاشر من رمضان")

        # Handle city analysis queries
        if "حلل المدينة" in user_query or "المناطق الناقصة" in user_query:
            return full_city_analysis(ramadan_data, "العاشر من رمضان")

        # Handle general queries
        print("Sending query to Gemini (Ramadan)")
        ramadan_chat_session.send_message(user_query)
        response = ramadan_chat_session.last.text
        
        # Enhance the response with specific details
        if "لا يوجد" in response or "غير متوفر" in response:
            return "🔍 لم أجد المعلومات المطلوبة بالضبط، لكن دعني أقدم لك معلومات عن المناطق المجاورة في العاشر من رمضان. هل يمكنك تحديد المنطقة التي تبحث عنها بشكل أدق؟"
        
        return response

    except Exception as e:
        print(f"❌ Error in chat_with_gemini_10th_ramadan: {str(e)}")
        return "⚠️ عذراً، حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى أو تقديم المزيد من التفاصيل عن المنطقة التي تبحث عنها."

def chat_with_gemini_madinaty(user_query):
    print(f"Processing Madinaty query: {user_query}")
    try:
        # Handle location-based queries
        lat_lon_match = re.search(r"خط العرض\s*([\d.]+)\s*وخ(ط)? الطول\s*([\d.]+)", user_query)
        if lat_lon_match:
            lat = float(lat_lon_match.group(1))
            lon = float(lat_lon_match.group(3))
            services, missing, area_info = get_services_near_location(lat, lon, city_data=madinaty_data)
            return format_service_response(services, missing, area_info, "مدينتي")

        # Handle city analysis queries
        if "حلل المدينة" in user_query or "المناطق الناقصة" in user_query:
            return full_city_analysis(madinaty_data, "مدينتي")

        # Handle general queries
        print("Sending query to Gemini (Madinaty)")
        madinaty_chat_session.send_message(user_query)
        response = madinaty_chat_session.last.text
        
        # Enhance the response with specific details
        if "لا يوجد" in response or "غير متوفر" in response:
            return "🔍 لم أجد المعلومات المطلوبة بالضبط، لكن دعني أقدم لك معلومات عن المناطق المجاورة في مدينتي. هل يمكنك تحديد المنطقة التي تبحث عنها بشكل أدق؟"
        
        return response

    except Exception as e:
        print(f"❌ Error in chat_with_gemini_madinaty: {str(e)}")
        return "⚠️ عذراً، حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى أو تقديم المزيد من التفاصيل عن المنطقة التي تبحث عنها."

def format_service_response(services, missing, area_info, city_name):
    if not services:
        return "لا توجد خدمات. هل تريد البحث في نطاق أوسع؟"

    # Get closest service of each type
    services_by_type = {}
    for s in services:
        if s["type"] not in services_by_type:
            services_by_type[s["type"]] = []
        services_by_type[s["type"]].append(s)
    
    # Format as direct list of services
    closest_services = [f"{s}: {min(services_by_type[s], key=lambda x: x['distance_km'])['name']}" 
                       for s in sorted(services_by_type.keys())]
    
    # Return in 2 lines max
    reply = f"{area_info or 'المنطقة'}: {', '.join(closest_services)}"
    if missing:
        reply += f"\nالخدمات المطلوبة: {', '.join(sorted(missing))}"
    
    return reply