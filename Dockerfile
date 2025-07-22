FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose the port the app runs on
EXPOSE 6789

# Create the SQLite database directory if it doesn't exist
RUN mkdir -p instance

# Command to run the application (for production using gunicorn)
CMD ["gunicorn", "--bind", "0.0.0.0:6789", "app:app"]
