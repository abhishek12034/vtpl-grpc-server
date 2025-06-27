# Use Python 3.10 as the base image
FROM python:3.10

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*  # Clean up apt cache to reduce image size

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the 'protos' directory and other necessary files into the container
COPY . .

# Generate the gRPC and protobuf Python files inside the 'stubs' directory
RUN python -m grpc_tools.protoc -I./protos --python_out=./stubs --grpc_python_out=./stubs ./protos/*.proto


# Expose the gRPC port
EXPOSE 50051

# Run the gRPC server
CMD ["python", "server.py"]
