import io
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from PIL import Image
from model import ml_model
import json

app = FastAPI(title="StyleSync ML Service")

class AnalyzeResponse(BaseModel):
    embedding: list[float]
    attributes: dict[str, str]

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_image(
    file: UploadFile = File(...),
    categories: str = Form(default='["shirt", "pants", "dress", "jacket", "shoes"]'),
    colors: str = Form(default='["black", "white", "red", "blue", "green", "neutral"]'),
    patterns: str = Form(default='["solid", "striped", "floral", "plaid", "graphic"]'),
    seasons: str = Form(default='["summer", "winter", "spring", "fall"]'),
    formality: str = Form(default='["casual", "business casual", "formal", "athletic"]')
):
    # Parse labels
    try:
        cat_labels = json.loads(categories)
        col_labels = json.loads(colors)
        pat_labels = json.loads(patterns)
        seas_labels = json.loads(seasons)
        form_labels = json.loads(formality)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format for label lists"}

    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data)).convert("RGB")

    # Get embeddings
    embedding = ml_model.get_embedding(image)

    # Get zero-shot classifications
    # Note: CLIP works best with descriptive sentences
    cat_preds = ml_model.zero_shot_classify(image, [f"a photo of a {c}" for c in cat_labels])
    col_preds = ml_model.zero_shot_classify(image, [f"a photo of a {c} clothing item" for c in col_labels])
    pat_preds = ml_model.zero_shot_classify(image, [f"a photo of a clothing item with {p} pattern" for p in pat_labels])
    seas_preds = ml_model.zero_shot_classify(image, [f"a photo of a clothing item for {s} weather" for s in seas_labels])
    form_preds = ml_model.zero_shot_classify(image, [f"a photo of a {f} clothing item" for f in form_labels])

    # Extract top prediction for each attribute
    def get_top(preds: dict, label_map: list[str]) -> str:
        # preds keys are the formatted string, values are probabilities
        # label_map is the original list
        best_formatted = max(preds, key=preds.get)
        # Find which original label it corresponds to (since we formatted them, we need to map back)
        # We can just check which label is in the formatted string, but it's simpler to index
        return next((label for label in label_map if label in best_formatted), "unknown")

    attributes = {
        "category": get_top(cat_preds, cat_labels),
        "color": get_top(col_preds, col_labels),
        "pattern": get_top(pat_preds, pat_labels),
        "season": get_top(seas_preds, seas_labels),
        "formality": get_top(form_preds, form_labels),
    }

    return {
        "embedding": embedding,
        "attributes": attributes
    }
