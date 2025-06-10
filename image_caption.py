# image_caption.py

import os
import torch
from PIL import Image
#from transformers import Blip2Processor, Blip2ForConditionalGeneration
from transformers import BlipProcessor, BlipForConditionalGeneration

# مسار مجلد الكاش المحلي اللي نقلته من Colab
# مسارات الموديل والـ processor اللي حفظتهم يدويًا
PROCESSOR_DIR = "E:\\Urban\\Urban-website\\blip_saved_model\\processor"
MODEL_DIR = "E:\\Urban\\Urban-website\\blip_saved_model\\model"

def generate_caption_with_display(image_path):
    """Generate caption for an image and return it"""
    try:
        # Load model and processor
        # تحميل من المسار المحلي المحفوظ مسبقًا
        processor = BlipProcessor.from_pretrained(PROCESSOR_DIR)
        model = BlipForConditionalGeneration.from_pretrained(MODEL_DIR)
        # Move model to GPU if available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)

        # Open and process image
        image = Image.open(image_path).convert("RGB")
        
        # Prepare image for model
        inputs = processor(images=image, return_tensors="pt").to(device, torch.float16)
        
        # Generate caption
        generated_ids = model.generate(**inputs, max_length=50)
        caption = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
        
        return caption

    except Exception as e:
        print(f"Error generating caption: {str(e)}")
        return None
