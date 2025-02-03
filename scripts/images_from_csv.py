import pandas as pd
import shutil
import os
import logging

# Setup logging
log_folder = './logs'
log_file = os.path.join(log_folder, 'images_from_csv.log')
os.makedirs(log_folder, exist_ok=True)

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Load CSV file into DataFrame
csv_file_path = './data/cleaned_data.csv'  # Update with your actual CSV path
df = pd.read_csv(csv_file_path)

# Define the target channels
target_channels = ["CheMed", "Lobelia pharmacy and cosmetics"]

# Filter the rows where 'channel_title' matches one of the target channels
filtered_df = df[df['channel_title'].isin(target_channels)]

# Ensure the 'images' folder exists, create it if not
images_folder = './images'
os.makedirs(images_folder, exist_ok=True)

# Loop through the filtered rows and copy the image files
for _, row in filtered_df.iterrows():
    media_path = row['media_path']
    filename = os.path.basename(media_path)

    try:
        shutil.copy(media_path, os.path.join(images_folder, filename))
        message = f"Copied {filename} to {images_folder}"
        print(message)
        logging.info(message)
    except FileNotFoundError:
        error_message = f"File not found: {media_path}"
        print(error_message)
        logging.warning(error_message)
    except Exception as e:
        error_message = f"Error copying {media_path}: {e}"
        print(error_message)
        logging.error(error_message)

print("Script completed!")
logging.info("Script completed successfully.")
