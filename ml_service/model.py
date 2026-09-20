import os
import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

MODEL_ID = "openai/clip-vit-base-patch32"

class MLModel:
    def __init__(self):
        # Allow use of CPU if CUDA not available, though for local dev CPU is fine for base CLIP
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained(MODEL_ID).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(MODEL_ID)
        
    def get_embedding(self, image: Image.Image) -> list[float]:
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
        # Normalize the embedding (optional but recommended for cosine similarity)
        image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
        return image_features.squeeze().tolist()

    def zero_shot_classify(self, image: Image.Image, candidate_labels: list[str]) -> dict:
        inputs = self.processor(
            text=candidate_labels, 
            images=image, 
            return_tensors="pt", 
            padding=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # This is the image-text similarity score
        logits_per_image = outputs.logits_per_image  
        probs = logits_per_image.softmax(dim=1).squeeze().tolist()
        
        return dict(zip(candidate_labels, probs))

# Singleton instance
ml_model = MLModel()
