from flask import Flask, request, render_template, jsonify
import openai
import base64
from io import BytesIO
from PIL import Image
import os

app = Flask(__name__, template_folder='templates', static_folder='static')

# OpenAI API anahtarını çevresel değişkenden al
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "Dosya bulunamadı"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Dosya seçilmedi"}), 400
    if file:
        # Dosyayı bellekte işleyin
        img = Image.open(file.stream)
        result = analyze_image(img)
        gtip_code = get_gtip_code(result)
        return jsonify({"description": result, "gtip_code": gtip_code})

def analyze_image(img):
    # Görüntüyü base64 formatına dönüştürme
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    payload = {
        "model": "gpt-4",
        "messages": [
            {
                "role": "user",
                "content": "Bu resimde ne var?",
                "image_url": f"data:image/jpeg;base64,{base64_image}"
            }
        ],
        "max_tokens": 150
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        try:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                # Yanıtı al ve döndür
                value = data['choices'][0].get('message', {}).get('content', 'İçerik bulunamadı')
                return value
            else:
                return "Yanıt beklenen formatta değil veya içerik bulunamadı."
        except Exception as e:
            return f"JSON ayrıştırma hatası: {str(e)}"
    else:
        return f"Hata: {response.status_code}, {response.text}"

def get_gtip_code(description):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    payload = {
        "model": "GPT-4o mini",
        "messages": [
            {
                "role": "user",
                "content": f"{description}. Bu ürün için GTIP kodu nedir?"
            }
        ],
        "max_tokens": 100
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        try:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                reply = data['choices'][0].get('message', {}).get('content', 'İçerik bulunamadı')
                gtip_code = reply.split(":")[-1].strip()
                return gtip_code
            else:
                return "Yanıt beklenen formatta değil veya içerik bulunamadı."
        except Exception as e:
            return f"JSON ayrıştırma hatası: {str(e)}"
    else:
        return f"Hata: {response.status_code}, {response.text}"

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"error": "Girdi sağlanmadı"}), 400

    try:
        # OpenAI API'si ile iletişim kurun
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": user_input}
            ],
            max_tokens=150
        )
        message_content = response['choices'][0]['message']['content']
        return jsonify({"message": message_content})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
