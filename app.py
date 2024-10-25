from flask import Flask, render_template, request, jsonify
from PIL import Image

import os
import base64
import json

import torch
from torchvision import transforms, models

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#загрузка модели
resnet = models.resnet101(pretrained=True)
resnet.eval()

#предобработка изображения
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

translations = {}

with open('imagenet_classes_ru.json', 'r', encoding='utf-8') as f:
    translations = json.load(f)

def translate_class(class_name):
    return translations.get(class_name, class_name)

@app.route('/upload-image', methods=['POST'])
def upload_image():
    data = request.get_json()
    if 'image' not in data:
        return jsonify({'error': 'No image provided'}), 400

    image_data = data['image']

    #если изображение в формате Base64, убираем префикс
    if image_data.startswith('data:image/png;base64,'):
        image_data = image_data.replace('data:image/png;base64,', '')
    elif image_data.startswith('data:image/jpeg;base64,'):
        image_data = image_data.replace('data:image/jpeg;base64,', '')

    #декодируем изображение
    try:
        image_bytes = base64.b64decode(image_data)
    except Exception as e:
        return jsonify({'error': 'Invalid image data'}), 400

    #сохраняем изображение на диск
    image_path = os.path.join(UPLOAD_FOLDER, 'image.jpg')
    with open(image_path, 'wb') as f:
        f.write(image_bytes)

    img = Image.open(image_path)
    img_t = transform(img)
    batch_t = torch.unsqueeze(img_t, 0)
    out = resnet(batch_t)

    _, indices = torch.sort(out, descending=True)
    percentage = torch.nn.functional.softmax(out, dim=1)[0] * 100

    with open('imagenet_classes.txt') as f:
        classes = [line.strip() for line in f.readlines()]

    #определяем наибльшую вероятность
    who = classes[indices[0][0]].split(",")[1][1:]
    probability = percentage[indices[0][0]].item()

    translated_who = translate_class(who)

    results = []
    results.append({'class': translated_who, 'probability': probability})

    with open('predictions.json', 'w') as json_file:
        json.dump(results, json_file, indent=4)
    
    return jsonify({'message': 'Image successfully uploaded', 'results': results})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=8080)