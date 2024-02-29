FROM python:3.11


# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app/server
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# Set the working directory in the container
RUN touch .env

# port
EXPOSE 80

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
