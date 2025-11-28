import modal
from pydantic import BaseModel
from typing import Dict, Any

# Define data models for validation
class SentimentRequest(BaseModel):
    text: str

class SentimentResponse(BaseModel):
    label: str
    score: float

app = modal.App("montewalk-sentiment")

# Define the image with necessary dependencies
image = (
    modal.Image.debian_slim()
    .pip_install(
        "transformers",
        "torch",
        "numpy",
        "fastapi"
    )
)

# Production settings:
# - min_containers=1: Keeps one container ready (reduces cold start latency)
# - scaledown_window=300: Shuts down after 5 mins of inactivity (saves cost)
# - @modal.concurrent: Handles multiple requests per container
@app.cls(
    image=image, 
    gpu="any", 
    timeout=600,
    min_containers=1,
    scaledown_window=300
)
@modal.concurrent(max_inputs=10)
class SentimentModel:
    """
    Production-ready FinBERT Sentiment Analysis Service.
    """
    
    def __enter__(self):
        """
        Load the model and tokenizer when the container starts.
        """
        from transformers import pipeline
        import torch
        
        print("Loading FinBERT model...")
        # Use a pipeline for easy inference
        # device=0 uses the first GPU
        device = 0 if torch.cuda.is_available() else -1
        self.pipe = pipeline("text-classification", model="ProsusAI/finbert", device=device)
        print("FinBERT model loaded successfully.")

    @modal.fastapi_endpoint(method="POST", docs=True)
    def predict(self, item: SentimentRequest) -> Dict[str, Any]:
        """
        Predict sentiment for a given text.
        
        Usage:
        POST /predict
        {
            "text": "The company reported record profits."
        }
        """
        text = item.text
        
        # Truncate text to avoid token limit errors (FinBERT max is 512 tokens)
        # Simple char truncation for safety
        if len(text) > 2000:
            text = text[:2000]
            
        try:
            # Run inference
            result = self.pipe(text)
            # result is a list of dicts: [{'label': 'positive', 'score': 0.9}]
            prediction = result[0]
            
            return {
                "label": prediction['label'],
                "score": prediction['score']
            }
        except Exception as e:
            print(f"Inference error: {e}")
            return {"error": "Internal inference error", "details": str(e)}


