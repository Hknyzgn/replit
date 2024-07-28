from flask import Flask, request, render_template, jsonify
import openai
from PIL import Image
import os
import base64
import requests
from io import BytesIO

app = Flask(__name__, template_folder='templates', static_folder='static')
    

# OpenAI API anahtarı
openai.api_key = 'sk-proj-brlgRioJzYDh4USOuHcxT3BlbkFJDxB1PmtYprZE0tKhbZzy'

# Vektör mağazası ve asistan ID'leri
vector_store_id = "vs_1N5yiB3FktibNA46NuqXrAVg"
assistant_id = "asst_wkduxKOfzM4iTUjIEZuDtHok"

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "Dosya bulunamadı"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Dosya seçilmedi"})
    if file:
        filename = file.filename
        file_path = os.path.join('uploads', filename)
        file.save(file_path)
        result = analyze_image(file_path)
        gtip_code = get_gtip_code(result)
        return jsonify({"description": result, "gtip_code": gtip_code})

def analyze_image(image_path):
    # Görüntüyü base64 formatına dönüştürme
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Bu resimde ne var?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 150
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        description = response.json()['choices'][0]['message']['content']
        return description
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
        # Sadece GTIP kodunu döndür
        reply = response.json()['choices'][0]['message']['content']
        gtip_code = reply.split(":")[-1].strip()
        return gtip_code
    else:
        return f"Hata: {response.status_code}, {response.text}"

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"error": "Girdi sağlanmadı"}), 400

    # Vektör Mağazası ile Asistanı Güncelle
    assistant = openai.beta.assistants.update(
        assistant_id=assistant_id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
    )

    # Bir İletişim Dizisi Oluştur
    thread = openai.beta.threads.create()
    print(f"Your thread id is - {thread.id}\n\n")

    message = openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input,
    )

    run = openai.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant.id
    )

    messages = list(openai.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))
    message_content = messages[0].content[0].text

    return jsonify({"message": message_content.value})

if not os.path.exists('uploads'):
    os.makedirs('uploads')

import os
app.run(debug=True, port=5000)
