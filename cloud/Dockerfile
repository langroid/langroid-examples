# Use an Ubuntu-based image with a more recent C++ compiler
FROM ubuntu:22.04

# Install build tools
RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get clean

# Install Python and pip
RUN apt-get install -y python3 python3-pip && \
    apt-get clean

# Set the working directory within the container
WORKDIR /app

# Copy the Python requirements file into the container
COPY requirements.txt .

# Load environment variables from .env file
ENV $(cat .env | grep -v ^# | xargs)

# Install any necessary dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

RUN pip install langroid

# Expose the port the application will run on
EXPOSE 8080

# Define the command to run your application
CMD ["python3", "server.py"]
