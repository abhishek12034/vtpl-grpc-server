# Use Python 3.10 as the base image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Generate the gRPC and protobuf Python files inside the 'stubs' directory
RUN python3 -m grpc_tools.protoc -I./protos --python_out=./stubs --grpc_python_out=./stubs ./protos/*.proto

# Set the PYTHONPATH environment variable to include /app so 'stubs' is discoverable
ENV PYTHONPATH=/app/stubs

# Expose the gRPC port
EXPOSE 50051

# Run the gRPC server
CMD ["python", "server.py"]
# addeing