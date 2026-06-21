import os
import cv2
import re
from datetime import datetime
from agents.vehicle_agent import VehicleAgent
from agents.triple_riding_agent import TripleRidingAgent
from agents.violation_agent import ViolationAgent
from agents.ocr_agent import OCRAgent
from agents.challan_agent import ChallanAgent
class Pipeline:
    def __init__(self):
        # Create directories
        os.makedirs("uploads", exist_ok=True)
        os.makedirs("outputs/evidence", exist_ok=True)
        os.makedirs("outputs/challans", exist_ok=True)
        self.vehicle_agent = VehicleAgent()
        self.triple_agent = TripleRidingAgent()
        self.violation_agent = ViolationAgent()
        self.ocr_agent = OCRAgent()
        self.challan_agent = ChallanAgent()
    def extract_plate_from_ocr(self, ocr_result):
        if not ocr_result:
            return None

        candidates = []

        # Format A: New PaddleX/PaddleOCR version (list of dicts containing 'rec_texts' and 'rec_scores')
        if isinstance(ocr_result, list) and len(ocr_result) > 0 and isinstance(ocr_result[0], dict):
            for res in ocr_result:
                texts = res.get('rec_texts', [])
                scores = res.get('rec_scores', [])
                for text, confidence in zip(texts, scores):
                    text_str = str(text).strip().replace(" ", "").upper()
                    # Strip special characters
                    clean_text = re.sub(r'[^A-Z0-9]', '', text_str)
                    if len(clean_text) >= 4 and len(clean_text) <= 12:
                        candidates.append((clean_text, float(confidence)))

        # Format B: Traditional PaddleOCR format (list of lists of [box, (text, confidence)])
        else:
            for line in ocr_result:
                if not line:
                    continue
                if isinstance(line, dict):
                    continue
                for res in line:
                    # res format: [ [ [x, y], ... ], (text, confidence) ]
                    if isinstance(res, (list, tuple)) and len(res) >= 2 and isinstance(res[1], (list, tuple)) and len(res[1]) >= 2:
                        text = str(res[1][0]).strip().replace(" ", "").upper()
                        confidence = res[1][1]

                        clean_text = re.sub(r'[^A-Z0-9]', '', text)
                        if len(clean_text) >= 4 and len(clean_text) <= 12:
                            candidates.append((clean_text, float(confidence)))

        if not candidates:
            return None

        # Regex pattern for Indian license plates: e.g. DL01AB1234 or MH12AB1234
        plate_pattern = re.compile(r'^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$')
        for text, conf in candidates:
            if plate_pattern.match(text):
                return text

        # General alphanumeric fallback
        for text, conf in candidates:
            if any(c.isalpha() for c in text) and any(c.isdigit() for c in text):
                return text

        # Sort by confidence
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]
    def run(self, image_path):
        # 1. Run vehicle agent (YOLO detection)
        results = self.vehicle_agent.detect(image_path)
        person_count = 0
        motorcycle_count = 0
        vehicle_boxes = []
        # Load image for cropping using OpenCV
        img = cv2.imread(image_path)
        h, w = (0, 0)
        if img is not None:
            h, w, _ = img.shape
        for box in results[0].boxes:
            cls = int(box.cls)
            if cls == 0:
                person_count += 1
            elif cls == 3:
                motorcycle_count += 1
            
            # Save bounding box coordinates for vehicles: 2 (car), 3 (motorcycle), 5 (bus), 7 (truck)
            if cls in [2, 3, 5, 7] and img is not None:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                # Constrain to image boundaries
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                if x2 > x1 and y2 > y1:
                    vehicle_boxes.append((x1, y1, x2, y2))
        # 2. Check for triple riding
        triple = self.triple_agent.detect(motorcycle_count, person_count)
        # 3. Generate violations
        violations = self.violation_agent.generate(triple)
        # 4. OCR Extraction for License Plate
        plate = None
        # Method A: Run OCR on the full image
        full_ocr = self.ocr_agent.read(image_path)
        plate = self.extract_plate_from_ocr(full_ocr)
        # Method B: If no plate detected from full image, crop vehicles and OCR them
        if (not plate or plate == "UNKNOWN") and img is not None:
            for idx, box in enumerate(vehicle_boxes):
                x1, y1, x2, y2 = box
                crop = img[y1:y2, x1:x2]
                if crop.size > 0:
                    temp_crop_path = f"outputs/evidence/temp_crop_{idx}.jpg"
                    cv2.imwrite(temp_crop_path, crop)
                    crop_ocr = self.ocr_agent.read(temp_crop_path)
                    
                    try:
                        os.remove(temp_crop_path)
                    except Exception:
                        pass
                    crop_plate = self.extract_plate_from_ocr(crop_ocr)
                    if crop_plate:
                        plate = crop_plate
                        break
        # Final plate fallback
        if not plate:
            plate = "NO PLATE DETECTED"
        # 5. Generate and save evidence image (annotated boxes)
        filename = os.path.basename(image_path)
        base_name, ext = os.path.splitext(filename)
        evidence_filename = f"evidence_{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        evidence_path = os.path.abspath(os.path.join("outputs", "evidence", evidence_filename))
        annotated_img = results[0].plot() # returns BGR numpy array
        cv2.imwrite(evidence_path, annotated_img)
        # 6. Generate challan PDF embedding the evidence image
        pdf = self.challan_agent.create(plate, violations, evidence_path)
        # Calculate risk score
        risk = 0
        if triple:
            risk += 40
        if len(violations) > 0:
            risk += 20 * len(violations)
        risk = min(risk, 100)
        return {
            "persons": person_count,
            "motorcycles": motorcycle_count,
            "violations": violations,
            "plate": plate,
            "pdf": pdf,
            "evidence": evidence_path,
            "risk": risk
        }