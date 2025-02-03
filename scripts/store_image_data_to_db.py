import os
import logging
import psycopg2
from sqlalchemy.engine.url import make_url
from dotenv import load_dotenv

load_dotenv("./.env")

DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    print("❌ DB_URL is not set. Please provide the connection URL in the .env file.")
    exit(1)

# Set up logging
log_folder = './logs'
os.makedirs(log_folder, exist_ok=True)
log_file = os.path.join(log_folder, 'store_image_to_db.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

labels_folder = './images/detected_images/labels/'

# PostgreSQL table creation query
CREATE_TABLE_QUERY = '''
CREATE TABLE IF NOT EXISTS image_data (
    id SERIAL PRIMARY KEY,
    file_name TEXT NOT NULL,
    object_name TEXT NOT NULL,
    confidence FLOAT NOT NULL,
    x_center FLOAT NOT NULL,
    y_center FLOAT NOT NULL,
    width FLOAT NOT NULL,
    height FLOAT NOT NULL
);
'''

# PostgreSQL insert query
INSERT_QUERY = '''
INSERT INTO image_data (file_name, object_name, confidence, x_center, y_center, width, height)
VALUES (%s, %s, %s, %s, %s, %s, %s);
'''

try:
    # Parse DB_URL and connect to PostgreSQL
    db_url = make_url(DB_URL)
    conn = psycopg2.connect(
        dbname=db_url.database, user=db_url.username, password=db_url.password,
        host=db_url.host, port=db_url.port
    )
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute(CREATE_TABLE_QUERY)
    conn.commit()
    logging.info("Connected to PostgreSQL and ensured table exists.")

    # Ensure labels folder exists
    if not os.path.exists(labels_folder):
        msg = f"Error: The folder '{labels_folder}' does not exist."
        print(msg)
        logging.error(msg)
    else:
        logging.info(f"Processing label files from {labels_folder}")

        for file in sorted(os.listdir(labels_folder)):
            file_path = os.path.join(labels_folder, file)

            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    if not lines:
                        msg = f"Warning: {file} is empty."
                        print(msg)
                        logging.warning(msg)
                        continue

                    for line in lines:
                        try:
                            parts = line.strip().split()
                            
                            # Object Name is everything before the first number
                            object_name = " ".join([p for p in parts if not p.replace('.', '', 1).isdigit()])
                            
                            # Extract Numeric Values
                            numbers = [float(p) for p in parts if p.replace('.', '', 1).isdigit()]

                            if len(numbers) == 5:  # Expected format
                                confidence, x_min, y_min, x_max, y_max = numbers

                                # Convert bounding box to center format (x_center, y_center, width, height)
                                x_center = (x_min + x_max) / 2
                                y_center = (y_min + y_max) / 2
                                width = x_max - x_min
                                height = y_max - y_min

                                cursor.execute(INSERT_QUERY, (file, object_name, confidence, x_center, y_center, width, height))

                            else:
                                msg = f"⚠ Error in {file}: Incorrect number of values -> {line.strip()}"
                                print(msg)
                                logging.error(msg)
                                continue

                        except ValueError as e:
                            msg = f"⚠ Error in {file}: Skipping malformed line -> {line.strip()} | {e}"
                            print(msg)
                            logging.error(msg)
                conn.commit()  # Commit after processing each file
            except Exception as e:
                msg = f"❌ Failed to process {file}: {e}"
                print(msg)
                logging.error(msg)

    # Close the connection
    cursor.close()
    conn.close()

    msg = "✅ Data successfully stored in PostgreSQL."
    print(msg)
    logging.info(msg)

except Exception as e:
    msg = f"❌ Database connection error: {e}"
    print(msg)
    logging.error(msg)
