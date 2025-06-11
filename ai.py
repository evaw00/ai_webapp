import torch
from torchvision import models, transforms
from PIL import Image
import os

# Model und Klassen einmal laden (global)
model = models.resnet50(pretrained=True)
model.eval()

# Pfad zur Klassen-Datei (Passe den Pfad ggf. an)
classes_file = 'imagenet_classes.txt'

# Klassen laden mit Sicherheit
if not os.path.exists(classes_file):
    raise FileNotFoundError(f"Die Datei {classes_file} wurde nicht gefunden.")

with open(classes_file) as f:
    classes = [line.strip() for line in f.readlines() if line.strip()]

if len(classes) == 0:
    raise ValueError("Die Klassenliste ist leer. Bitte überprüfe die Datei.")

# Bildtransformationen für ResNet
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def classify_image(image_path):
    print(f"Klassifiziere Bild: {image_path}")
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Bilddatei nicht gefunden: {image_path}")

    img = Image.open(image_path).convert('RGB')
    print(f"Bildgröße: {img.size}")

    img_t = transform(img)
    batch_t = torch.unsqueeze(img_t, 0)

    with torch.no_grad():
        outputs = model(batch_t)

    print(f"Model Output Shape: {outputs.shape}")
    
    if outputs.shape[0] == 0:
        raise ValueError("Model liefert keine Ausgaben.")

    _, predicted_idx = torch.max(outputs, 1)

    if predicted_idx.numel() == 0:
        raise ValueError("Vorhersage-Index ist leer.")

    predicted_idx = predicted_idx.item()
    print(f"Vorhergesagte Klasse Index: {predicted_idx}")

    if predicted_idx >= len(classes):
        raise IndexError(f"Vorhergesagte Klasse {predicted_idx} ist außerhalb des Bereichs.")

    predicted_class = classes[predicted_idx]

    # Vereinfachte Erklärung (Dummy)
    explanation = f"Das Bild wurde als '{predicted_class}' klassifiziert, weil das Modell hohe Wahrscheinlichkeiten für diese Kategorie berechnet hat."

    return predicted_class, explanation

