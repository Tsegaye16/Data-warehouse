# Use an official Python image
FROM python:3.9

# Set working directory
WORKDIR /app

# Copy the backend code
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose backend port
EXPOSE 8000

# Run `app.py` (which internally starts the backend and scraper)
CMD ["python", "main.py"]
