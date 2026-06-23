import os
import easyocr
import torch

class OCRAgent:

    def __init__(self):
        # Use GPU if available via PyTorch
        use_gpu = torch.cuda.is_available()
        
        try:
            # Initialize EasyOCR with English language
            self.reader = easyocr.Reader(['en'], gpu=use_gpu)
        except Exception as e:
            print(f"Error initializing EasyOCR: {e}")
            self.reader = None

    def read(self, image_path):
        if not self.reader:
            return None
            
        try:
            # EasyOCR returns a list of tuples: (bounding_box, text, confidence)
            result = self.reader.readtext(image_path)
            return result
        except Exception as e:
            print(f"EasyOCR read error on {image_path}: {e}")
            return None