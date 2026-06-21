import os
# Disable MKLDNN globally to fix oneDNN PIR attribute compatibility crash in PaddlePaddle
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"

from paddleocr import PaddleOCR

class OCRAgent:

    def __init__(self):
        device = 'cpu'
        try:
            import paddle
            if paddle.device.is_compiled_with_cuda():
                device = 'gpu'
        except Exception as e:
            print(f"Error checking paddle GPU compilation: {e}")

        # Initialize PaddleOCR with device and lang parameters only
        self.ocr = PaddleOCR(device=device, lang='en')

    def read(self, image_path):
        try:
            # Under new PaddleX-based PaddleOCR, we can call predict() or ocr()
            # Let's call ocr() and handle any return format in the pipeline parser
            result = self.ocr.ocr(image_path)
            return result
        except Exception as e:
            print(f"PaddleOCR read error on {image_path}: {e}")
            return None