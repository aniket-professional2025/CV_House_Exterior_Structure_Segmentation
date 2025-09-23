# Importing Required Packages
import os
import json
import datetime
import numpy as np
import cv2
from svgpathtools import parse_path
import pycocotools.mask as maskUtils
import pandas as pd

def process_paths_to_json(paths_dict: dict, output_filepath: str):
    """
    Processes a dictionary of SVG path data strings and generates a single
    JSON annotation file suitable for SAM fine-tuning.

    Args:
        paths_dict (dict): A dictionary where keys are category names and
                           values are the raw SVG path data strings.
        output_filepath (str): The full path to save the output JSON file.
    """
    print(f"Processing paths for output file: {os.path.basename(output_filepath)}")

    width, height = 1024, 1024  # Standard image size for SAM
    annotations = []
    ann_id = 0

    # Iterate through the categories and their SVG path data strings
    for category_name, path_data in paths_dict.items():
        if not path_data:
            print(f"Warning: Skipping category '{category_name}'. Path data is empty.")
            continue

        try:
            # Directly parse the SVG path data string
            path_obj = parse_path(path_data)
            pts = []
            
            # Sample points along the SVG path
            for seg in path_obj:
                # Use fewer points for simplification to decrease processing time
                for t in np.linspace(0, 1, 25): 
                    point = seg.point(t)
                    pts.append([point.real, point.imag])
            pts = np.array(pts, dtype=np.int32)

            # Simplify the polygon using the Douglas-Peucker algorithm
            epsilon = 0.005 * cv2.arcLength(pts, True)
            simplified_pts = cv2.approxPolyDP(pts, epsilon, True)

            # create mask with the simplified points
            mask = np.zeros((height, width), dtype=np.uint8)
            cv2.fillPoly(mask, [simplified_pts], 1)

            # bounding box
            x, y, w, h = cv2.boundingRect(simplified_pts)

            # area
            area = float(cv2.contourArea(simplified_pts))

            # segmentation (RLE)
            rle = maskUtils.encode(np.asfortranarray(mask.astype(np.uint8)))
            rle["counts"] = rle["counts"].decode("utf-8")

            annotations.append({
                "id": ann_id,
                "category": category_name,
                "bbox": [float(x), float(y), float(w), float(h)],
                "area": area,
                "segmentation": rle
            })
            ann_id += 1

        except Exception as e:
            print(f"Skipping path for category '{category_name}' due to error: {e}")
            continue

    # Save JSON file
    json_data = {
        "image": {
            "image_id": 0,
            "license": 1,
            "file_name": os.path.basename(output_filepath).replace('.json', '.jpg'),
            "height": height,
            "width": width,
            "date_captured": datetime.datetime.now().isoformat(),
            "extra": {"name": os.path.basename(output_filepath).replace('.json', '.jpg')}
        },
        "annotations": annotations
    }

    with open(output_filepath, "w") as f:
        json.dump(json_data, f, indent=4)
    
    print(f"Processing finished for file: {os.path.basename(output_filepath)}")

if __name__ == "__main__":
    input_excel_file = 'CompleteData.xlsx'
    output_dir = 'Outputs'

    try:
        df = pd.read_excel(input_excel_file)
        print(f"Successfully read data from {input_excel_file}. Found {len(df)} entries.")
    except FileNotFoundError:
        print(f"Error: The file '{input_excel_file}' was not found.")
        exit()
    except Exception as e:
        print(f"An error occurred while reading the Excel file: {e}")
        exit()

    if 'paths' not in df.columns or 'id' not in df.columns:
        print("Error: The Excel file must contain 'paths' and 'id' columns.")
        exit()

    os.makedirs(output_dir, exist_ok=True)
    print(f"Created output directory: {output_dir}")

    for index, row in df.iterrows():
        try:
            paths_str = row['paths']
            paths_dict = json.loads(paths_str)
            name = row['id']
            
            output_filename = f"Image_{index + 1}.json"
            output_filepath = os.path.join(output_dir, output_filename)
            
            process_paths_to_json(paths_dict, output_filepath)
        
        except json.JSONDecodeError:
            print(f"Warning: Skipping row {index} due to invalid JSON in 'Paths' column.")
            continue
        except KeyError as e:
            print(f"Warning: Skipping row {index}. Missing expected key in Paths dictionary: {e}")
            continue
        except Exception as e:
            print(f"An unexpected error occurred while processing row {index}: {e}")
            continue

    print("\nAll processing complete.")