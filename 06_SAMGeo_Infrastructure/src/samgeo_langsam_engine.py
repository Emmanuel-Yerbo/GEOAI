"""
SAMGeo & LangSAM Inference Engine
Author: Emmanuel Yerbo
Applies Meta's Segment Anything Model (SAM) and LangSAM for prompt-based feature extraction.
"""
from samgeo import SamGeo
from samgeo.text_sam import LangSAM

def initialize_samgeo(model_type="vit_h", checkpoint=None):
    """Initializes SAMGeo zero-shot segmentation model."""
    sam = SamGeo(model_type=model_type, checkpoint=checkpoint)
    return sam

def detect_aircraft_with_langsam(image_path, text_prompt="Airplanes", box_threshold=0.3, text_threshold=0.25):
    """
    Applies Grounding DINO + SAM for natural language prompted aviation detection.
    """
    model = LangSAM()
    model.predict(image_path, text_prompt, box_threshold=box_threshold, text_threshold=text_threshold)
    return model
