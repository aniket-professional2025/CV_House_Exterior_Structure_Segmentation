# Importing Required Packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import supervision as sv
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
import torch

# Set the devivce
DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

# SAM Model Type and checkpoint path
model_type = 'vit_h'
checkpoint_path = r"C:\Users\Webbies\Jupyter_Notebooks\Berger_Exterior_Segmentation\sam_vit_h_4b8939.pth"

# Creating the SAM model
sam = sam_model_registry[model_type](checkpoint = checkpoint_path).to(device = DEVICE)

# Define a function to generate the segmentation masks
def mask_generator_sam(image_path):
    mask_generator = SamAutomaticMaskGenerator(sam)
    image_path = image_path
    image_bgr = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    sam_result = mask_generator.generate(image_rgb)
    mask_annotator = sv.MaskAnnotator(color_lookup=sv.ColorLookup.INDEX)
    detections = sv.Detections.from_sam(sam_result=sam_result)
    annotated_image = mask_annotator.annotate(scene=image_bgr.copy(), detections=detections)
    sv.plot_image(annotated_image, (8,8))

# Inferencing with the function
path = r"C:\Users\Webbies\Jupyter_Notebooks\Berger_Exterior_Segmentation\Berger_Images_04June\Berger_New_Image_28.jpg"
mask_generator_sam(path)