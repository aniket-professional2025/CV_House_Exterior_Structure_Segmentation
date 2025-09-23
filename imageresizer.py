# Importing Required Packages
import os
from PIL import Image

# Define a function to resize the Images in to 1024*1024
def resize_images(directory, size=(1024, 1024)):
    
    print(f"Starting image resizing process in directory: {directory}")
    
    # Check if the directory exists
    if not os.path.isdir(directory):
        print(f"Error: The directory '{directory}' does not exist.")
        return

    # List all files in the directory
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            filepath = os.path.join(directory, filename)
            try:
                # Open the image file
                with Image.open(filepath) as img:
                    print(f"Resizing '{filename}'...")
                    
                    # Resize the image
                    resized_img = img.resize(size, Image.Resampling.LANCZOS)
                    
                    # Save the resized image, overwriting the original
                    resized_img.save(filepath, "JPEG")
                    print(f"Successfully resized and saved '{filename}'.")
                    
            except Exception as e:
                print(f"Failed to process '{filename}'. Error: {e}")

    print("\nAll image processing complete.")

if __name__ == "__main__":
    # Define the directory to process
    outputs_folder = "Outputs"
    
    # Call the function to start the process
    resize_images(outputs_folder)