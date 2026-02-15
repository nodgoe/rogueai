# Use a slim Python image
FROM python:3.14-rc-slim

# Install necessary system packages for curses
RUN apt-get update && apt-get install -y \
    libncursesw5-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the script
COPY main.py .

# Run the application
CMD ["python3", "main.py"]
