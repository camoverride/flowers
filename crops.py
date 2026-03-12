import cv2
import os
import random

# Parameters
input_folder = "uncropped_images"
output_folder = "cropped_images"
final_width, final_height = 480, 800
crop_width, crop_height = final_width * 2, final_height * 2
crops_per_image = 5

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Loop through images
for filename in os.listdir(input_folder):
    file_path = os.path.join(input_folder, filename)
    
    # Read image
    img = cv2.imread(file_path)
    if img is None:
        continue

    h, w, _ = img.shape

    # Skip images smaller than the crop size
    if w < crop_width or h < crop_height:
        continue

    for i in range(crops_per_image):
        # Random top-left corner for the crop
        x = random.randint(0, w - crop_width)
        y = random.randint(0, h - crop_height)
        
        crop = img[y:y+crop_height, x:x+crop_width]
        
        # Resize crop down to final dimensions
        resized_crop = cv2.resize(crop, (final_width, final_height))
        
        # Save crop
        crop_filename = f"{os.path.splitext(filename)[0]}_crop{i+1}.jpg"
        cv2.imwrite(os.path.join(output_folder, crop_filename), resized_crop)

print("Cropping and resizing done!")