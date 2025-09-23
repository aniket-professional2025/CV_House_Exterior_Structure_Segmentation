# # For Processing single Files
# from svgtoroboflow import svg_to_image_and_json
# path = r"C:\Users\anike\JUPYTER_NOTEBOOKS\WEBBIES\CV_House_Exterior_Structure_Segmentation-main\image_1720596516947-01.svg"
# svg_to_image_and_json(path, output_dir = 'outputs')

# Importing Required Packages
from svgtoroboflow import svg_to_image_and_json
import os

# Inference step
input_dir = "SVGs"
output_dir = "output" # You can change this to any directory you want

# Check if the Input Directory Exists or Not
if not os.path.isdir(input_dir):
    print(f"Error: The directory '{input_dir}' does not exist.")
    print("Please create an 'SVGs' folder and place your SVG files inside.")

    # If the Input Directory Exists then go to the next step
else:
    
    # Check if the SVG files are present or not

    svg_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".svg")]
    if not svg_files:
        print(f"No SVG files found in '{input_dir}'.")

        # If the SVG files are found, go to the next step
    else:
        print(f"Found {len(svg_files)} SVG files to process.")
        for file_name in svg_files:
            file_path = os.path.join(input_dir, file_name)
            print(f"\n--- Starting processing file: {file_name} ---")
            try:
                svg_to_image_and_json(file_path, output_dir)
                print(f"--- Processing finished for file: {file_name} ---")
            except Exception as e:
                print(f"--- Error processing file: {file_name} ---")
                print(f"Error details: {e}")