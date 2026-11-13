# Use Python 3.11.4 base image
FROM python:3.11.4-slim

# Set working directory
WORKDIR /app

# Copy all project files and folders
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for Streamlit (default 8501)
EXPOSE 80

# Run the Streamlit app
CMD ["streamlit", "run", "app/main.py", "--server.port=80", "--server.address=0.0.0.0"]
