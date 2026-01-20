# Use a minimal Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system packages required for psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the port Flask will run on (default is 5000)
EXPOSE 5000

# Run the Flask app
CMD ["python", "server.py"]
#CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "server:app"]