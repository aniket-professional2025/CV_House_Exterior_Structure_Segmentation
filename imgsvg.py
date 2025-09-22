# Importing Required Packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import supervision as sv
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
import svgwrite
from skimage import measure
import torch
import uuid
import os
import io
from skimage.measure import approximate_polygon
from torch.cuda.nccl import unique_id

# Set the devivce
DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

# SAM Model Type and checkpoint path
model_type = 'vit_h'
checkpoint_path = r"C:\Users\Webbies\Jupyter_Notebooks\Berger_Exterior_Segmentation\sam_vit_h_4b8939.pth"

# Creating the SAM model
sam = sam_model_registry[model_type](checkpoint = checkpoint_path).to(device = DEVICE)

# Use the SamAutomaticMaskGenerator to generate the masks
mask_generator = SamAutomaticMaskGenerator(sam)

# Create a helper function image_svg_without_noise to create Raster images to svg format (redefined helper function)
def masks_to_svg(masks, output_filepath):
    dwg = svgwrite.Drawing(output_filepath, size = ("1080px", "810px"), profile = 'tiny')
    for i, mask in enumerate(masks):
        # Clean the mask using morphological operations
        mask_uint8 = (mask.astype(np.uint8) * 255)
        kernel = np.ones((3, 3), np.uint8)
        cleaned_mask = cv2.morphologyEx(mask_uint8, cv2.MORPH_OPEN, kernel)
        cleaned_mask = cv2.morphologyEx(cleaned_mask, cv2.MORPH_CLOSE, kernel)
        # Extract contours from the cleaned mask
        contours = measure.find_contours(cleaned_mask.astype(int), 0.5)
        for contour in contours:
            # Simplify contour using Ramer–Douglas–Peucker algorithm
            simplified_contour = approximate_polygon(contour, tolerance = 2.0)
            if len(simplified_contour) < 3:
                continue  # Skip if not enough points to form a shape
            # Build SVG path from simplified contour
            path_data = f"M{simplified_contour[0, 1]},{simplified_contour[0, 0]}"
            for point in simplified_contour[1:]:
                path_data += f" L{point[1]},{point[0]}"
            path_data += " Z"
            # Create an SVG path element.
            stroke_colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown',
                             'cyan', 'magenta', 'yellow', 'lime', 'teal', 'olive']
            stroke_color = stroke_colors[i % len(stroke_colors)]  # Cycle through colors
            # path = dwg.path(d=path_data, fill = 'none', stroke = stroke_color, stroke_width = 1)
            path = dwg.path(d = path_data, fill = 'lightblue', stroke = stroke_color, fill_opacity = 0.4, stroke_width = 2)
            # Add the path element to the SVG drawing.
            dwg.add(path)
    # Save the complete SVG drawing to the output file.
    dwg.save()
    print(f"All mask paths saved to a single SVG file: {output_filepath}")

# Define a function so convert the masks into svg with the above helper function
def sam_mask_svg_generation(image_path): # image_url
  image_bgr = cv2.imread(image_path)
  image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
  sam_result = mask_generator.generate(image_rgb)
  mask_annotator = sv.MaskAnnotator(color_lookup=sv.ColorLookup.INDEX)
  detections = sv.Detections.from_sam(sam_result=sam_result)
  annotated_image = mask_annotator.annotate(scene=image_bgr.copy(), detections=detections)
  masks = [mask['segmentation'] for mask in sorted(sam_result, key = lambda x: x['area'], reverse = True)]
  output_dir = "Extracted_MaskImage_SVG"
  os.makedirs(output_dir, exist_ok=True)
  unique_id = str(uuid.uuid4())[:8]
  output_filepath = os.path.join(output_dir, f"mask_{unique_id}.svg")
  masks_to_svg(masks, output_filepath)


##### To change the naming pattern of the mask paths
##### Use this instead of unique_id......................second last part
# existing_svgs = [f for f in os.listdir(output_dir) if f.endswith('.svg')]
# next_index = len(existing_svgs) + 1
# output_filepath = os.path.join(output_dir, f"mask_{next_index}.svg")
