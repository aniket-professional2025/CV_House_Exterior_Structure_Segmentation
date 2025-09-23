# Importing Required Packages
import os
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

# Define function That takes the Excel file and a directory to store the Images in jpg format
def download_images_from_excel(excel_file: str, output_dir: str):
    
    try:
        # Read the Excel file into a pandas DataFrame
        df = pd.read_excel(excel_file)
        print(f"Successfully read data from {excel_file}. Found {len(df)} entries.")
    except FileNotFoundError:
        print(f"Error: The file '{excel_file}' was not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the Excel file: {e}")
        return

    # Check if 'ImageURL' and 'Name' columns exist
    if 'imageUploaded' not in df.columns or 'id' not in df.columns:
        print("Error: The Excel file must contain 'imageUploaded' and 'id' columns.")
        return

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # Iterate through the DataFrame rows
    for index, row in df.iterrows():
        image_url = row['imageUploaded']
        name = row['id']
        
        # Create the filename as Image_1.jpg, Image_2.jpg, etc.
        filename = f"Image_{index + 1}.jpg"
        filepath = os.path.join(output_dir, filename)

        try:
            print(f"Downloading image for '{name}' from {image_url}...")
            # Send a GET request to the image URL
            response = requests.get(image_url, timeout=10)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Use BytesIO to handle image in memory without saving first
                image_data = BytesIO(response.content)
                img = Image.open(image_data)

                # Convert RGBA to RGB if necessary before saving as JPEG
                if img.mode == 'RGBA':
                    img = img.convert('RGB')

                # Resize the image to 1024x1024 pixels
                resized_img = img.resize((1024, 1024), Image.Resampling.LANCZOS)

                # Save the Resized Image
                resized_img.save(filepath, "JPEG")
                print(f"Successfully downloaded, resized, and saved: {filename}")
            else:
                print(f"Failed to download image from {image_url}. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while downloading image for '{name}': {e}")
        
    print("\nAll image processing complete.")

if __name__ == "__main__":
    # Define your input file and output directory
    input_excel_file = 'CompleteData.xlsx'
    output_images_dir = 'Outputs'

    # Call the function to start the process
    download_images_from_excel(input_excel_file, output_images_dir)