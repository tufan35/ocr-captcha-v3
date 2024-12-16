from transformers import VisionEncoderDecoderModel, TrOCRProcessor
import torch
from PIL import Image
import io
import base64
from flask import Flask, request, jsonify

app = Flask(__name__)

processor = TrOCRProcessor.from_pretrained("anuashok/ocr-captcha-v3")
model = VisionEncoderDecoderModel.from_pretrained("anuashok/ocr-captcha-v3")

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    if 'image' not in data:
        return jsonify({'error': 'No image provided'}), 400

    try:
        image_data = base64.b64decode(data['image'])
        image = Image.open(io.BytesIO(image_data)).convert("RGBA")

        background = Image.new("RGBA", image.size, (255, 255, 255))
        combined = Image.alpha_composite(background, image).convert("RGB")

        pixel_values = processor(combined, return_tensors="pt").pixel_values.to(device)

        generated_ids = model.generate(pixel_values)
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        return jsonify({'text': generated_text}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
