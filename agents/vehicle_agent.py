import os
import shutil
from ultralytics import YOLO
class VehicleAgent:
    def __init__(self):
        os.makedirs("models/detection", exist_ok=True)
        
        # Check standard locations for models
        model_paths = [
            "models/detection/yolo11n.pt",
            "models/detection/yolo26s.pt",
            "yolo11n.pt",
            "yolo26s.pt"
        ]
        
        self.model = None
        for path in model_paths:
            if os.path.exists(path):
                try:
                    self.model = YOLO(path)
                    print(f"Loaded YOLO model from: {path}")
                    break
                except Exception as e:
                    print(f"Error loading model from {path}: {e}")
        
        # Fallback: Download yolo11n.pt if no model is loaded
        if self.model is None:
            print("No local model found. Downloading yolo11n.pt...")
            try:
                self.model = YOLO("yolo11n.pt")
                # Move downloaded model to models/detection for clean structure
                if os.path.exists("yolo11n.pt"):
                    shutil.move("yolo11n.pt", "models/detection/yolo11n.pt")
                    self.model = YOLO("models/detection/yolo11n.pt")
                    print("YOLO model downloaded and saved to models/detection/yolo11n.pt")
            except Exception as e:
                print(f"Failed to download/load YOLO model: {e}")
                # Try to load YOLO with default argument just in case
                self.model = YOLO("yolo11n.pt")
    def detect(self, image):
        results = self.model(image)
        return results