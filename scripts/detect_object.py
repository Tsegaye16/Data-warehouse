import cv2
import torch
import os
import logging

# Set up logging
logging.basicConfig(
    filename="./logs/object_detect.log",  # Log file
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Load the pre-trained YOLOv5 model
logging.info("Loading YOLOv5 model...")
try:
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=True)
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Failed to load model: {e}")
    exit(1)

# Define input and output folders
input_folder = "./images"  # Change this to your images folder path
output_folder = "./images/detected_images"
label_folder = "./images/detected_images/labels"

# Create output directories if they don't exist
os.makedirs(output_folder, exist_ok=True)
os.makedirs(label_folder, exist_ok=True)

# Process each image in the folder
logging.info(f"Processing images in '{input_folder}' folder...")
for filename in os.listdir(input_folder):
    if filename.endswith((".jpg", ".jpeg", ".png")):  # Process only image files
        image_path = os.path.join(input_folder, filename)
        output_image_path = os.path.join(output_folder, filename)
        label_file_path = os.path.join(label_folder, filename.rsplit('.', 1)[0] + ".txt")

        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                logging.warning(f"Skipping {filename}: Unable to read image.")
                continue

            # Run YOLO object detection
            logging.info(f"Running detection on {filename}...")
            results = model(img)

            # Prepare label data
            label_data = []

            # Process detection results
            for *xyxy, conf, cls in results.xyxy[0]:  # Get bounding box, confidence, and class label
                x1, y1, x2, y2 = map(int, xyxy)  # Convert coordinates to integers
                confidence = conf.item()
                class_name = model.names[int(cls)]  # Convert class index to class name
                
                # Store label data
                label_data.append(f"{class_name} {confidence:.2f} {x1} {y1} {x2} {y2}\n")

                # Draw bounding box and label on the image
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green bounding box
                cv2.putText(img, f"{class_name} {confidence:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Save the detected image
            cv2.imwrite(output_image_path, img)
            logging.info(f"Saved detected image: {output_image_path}")

            # Save labels to a text file
            with open(label_file_path, "w") as label_file:
                label_file.writelines(label_data)
            logging.info(f"Saved labels for {filename}: {len(label_data)} objects detected.")

        except Exception as e:
            logging.error(f"Error processing {filename}: {e}")

logging.info("Object detection completed. Check 'detected_images' and 'labels' folders.")
print("Object detection completed. Logs are saved in 'object_detection.log'.")
