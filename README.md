# gRPC Server for Image Enhancement Algorithms

## Project Overview
This project is focused on building a gRPC server that exposes a collection of image enhancement algorithms. The server allows clients to perform various image processing tasks remotely through gRPC-based communication.


## Requirements
- **Python3.10**: 
## Installation and Setup locally for Linux
1. Clone the repository:
   ```bash
   git clone https://github.com/abhishek12034/vtpl-grpc-server.git
   ```
   ```bash
   python3 -m venv .venv
   ```
    ```bash
    source .venv/bin/active
   ```
     ```bash
    pip install -r requirements.txt
   ```
   # Set the path according to your system
   ```
export PYTHONPATH=$PYTHONPATH:/home/vadmin/Documents/vtpl_grpc_server/stubs
   ```
    ```
    python3 server.py
    ```
    ### For Generating python code from  Proto file
    ```bash
    python3 -m grpc_tools.protoc -I./protos --python_out=./stubs --grpc_python_out=./stubs ./protos/*.proto
    ```
   

   ## Setup using Docker 
   ```bash
    docker build -t grpc-server .
    ```
    ``` bash
    docker run -p 50051:50051 grpc-server
    ```
