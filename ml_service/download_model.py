import os
from transformers import CLIPProcessor, CLIPModel

# Set environment variable so transformers caches in the app directory during docker build
os.environ['TRANSFORMERS_CACHE'] = '/app/models'

MODEL_ID = "openai/clip-vit-base-patch32"

print(f"Downloading model {MODEL_ID}...")
model = CLIPModel.from_pretrained(MODEL_ID)
processor = CLIPProcessor.from_pretrained(MODEL_ID)
print("Model downloaded and cached successfully.")
