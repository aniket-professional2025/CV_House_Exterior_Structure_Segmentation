# Importing Required Packages
from svgtoroboflow import svg_to_image_and_json

# Inference step
path = r"C:\Users\Webbies\Jupyter_Notebooks\Berger_Exterior_Segmentation\image_1720596516947-01.svg"
svg_to_image_and_json(path, output_dir = "SvgToRbfSAM")