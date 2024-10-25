import torch
from torchvision import transforms, models
from PIL import Image
import json

resnet = models.resnet101(pretrained=True)

resnet.eval()

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Загрузка входного изображения
img = Image.open("uploads/image.jpg")

# Предобработка изображения
img_t = transform(img)
batch_t = torch.unsqueeze(img_t, 0)

# Выполнение инференции модели
out = resnet(batch_t)

# Получение топ-5 предсказанных классов
_, indices = torch.sort(out, descending=True)
percentage = torch.nn.functional.softmax(out, dim=1)[0] * 100

# Загрузка меток классов ImageNet
with open('imagenet_classes.txt') as f:
    classes = [line.strip() for line in f.readlines()]

who = classes[indices[0][0]].split(",")[1][1:]
probability = percentage[indices[0][0]].item()

results = []
results.append({'class': who, 'probability': probability})

# Запись результатов в JSON-файл
with open('predictions.json', 'w') as json_file:
    json.dump(results, json_file, indent=4)

print(f"{who}: {probability}%")