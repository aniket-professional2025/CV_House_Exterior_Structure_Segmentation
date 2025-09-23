# Importing Required Packages
import os
import json
import datetime
import base64
from xml.dom import minidom
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
from svgpathtools import parse_path
import pycocotools.mask as maskUtils

# Function to convert svg image into a RoboFlow style SAM dataset
def svg_to_image_and_json(svg_paths, output_dir = "."):
    """
    Convert one or multiple SVG files into a 1024x1024 JPG image
    and corresponding JSON annotations.

    Args:
        svg_paths (list[str] or str): List of SVG file paths or single path.
        output_dir (str): Directory where outputs will be saved.

    Returns:
        results (list[dict]): List of results with keys: svg, image, json
    """
    if isinstance(svg_paths, str):
        svg_paths = [svg_paths]

    results = []
    for svg_path in svg_paths:
        print(f"Processing {svg_path} ...")
        doc = minidom.parse(svg_path)

        # Find The Image Path
        print("[DEBUG] Finding the Base64 Encoded Image Path")
        layer1 = None
        for g in doc.getElementsByTagName("g"):
            if g.getAttribute("id") == "Layer_1":
                layer1 = g
                break

        base_img = None
        if layer1:
            images = layer1.getElementsByTagName("image")
            if images:
                href = images[0].getAttribute("xlink:href") or images[0].getAttribute("href")
                if href and href.startswith("data:image"):
                    b64data = href.split(",")[1]
                    imgdata = base64.b64decode(b64data)
                    base_img = Image.open(BytesIO(imgdata)).convert("RGB")
                    base_img = base_img.resize((1024, 1024))
        
        if base_img is None:
            doc.unlink()
            raise RuntimeError(f"No base64 image found in {svg_path}")
        
        print("[DEBUG] Image Processing Completed")

        # Output filenames
        base_name = os.path.splitext(os.path.basename(svg_path))[0]
        output_img = os.path.join(output_dir, f"{base_name}.jpg")
        output_json = os.path.join(output_dir, f"{base_name}.json")

        # make sure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Save image
        base_img.save(output_img, "JPEG")
        width, height = base_img.size

        # Extract vector annotations
        print("[DEBUG] Finding Other Categories for Encoding")
        groups = doc.getElementsByTagName("g")
        annotations = []
        ann_id = 0

        for g in groups:
            gid = g.getAttribute("id").strip().lower()
            if gid == "layer_1":
                continue  # skip raster layer

            paths = g.getElementsByTagName("path")
            for p in paths:
                d = p.getAttribute("d")
                if not d:
                    continue

                try:
                    path_obj = parse_path(d)
                    pts = []
                    for seg in path_obj:
                        for t in np.linspace(0, 1, 25): # Original is 50
                            point = seg.point(t)
                            pts.append([point.real, point.imag])
                    pts = np.array(pts, dtype=np.int32)

                    # Simplify the polygon using the Douglas-Peucker algorithm
                    # This step is added to decrease the length of the counts parameter
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
                        "category": gid,
                        "bbox": [float(x), float(y), float(w), float(h)],
                        "area": area,
                        "segmentation": rle
                    })
                    ann_id += 1

                except Exception as e:
                    print(f"Skipping path in {gid} due to error: {e}")
                    continue

        doc.unlink()
        print("[DEBUG] All Required Categories Found Succesfully")

        # Save JSON
        json_data = {
            "image": {
                "image_id": 0,
                "license": 1,
                "file_name": os.path.basename(output_img),
                "height": height,
                "width": width,
                "date_captured": datetime.datetime.now().isoformat(),
                "extra": {"name": os.path.basename(output_img)}
            },
            "annotations": annotations
        }

        with open(output_json, "w") as f:
            json.dump(json_data, f, indent = 4)

        print(f"Saved: {output_img}, {output_json}")
        results.append({"image": output_img, "json": output_json})


    return results