#!/bin/bash

# Define variables
REPO_URL="git@github.com:abhishek12034/vtpl-grpc-server.git"  # Git repository URL with token
REPO_DIR="vtpl-grpc-server"  # Local directory name after cloning
VENV_DIR=".venv"                # Virtual environment folder name
SERVER_SCRIPT="server.py"      # Replace with your Python server script name

# Check if the repository is already cloned
if [ ! -d "$REPO_DIR" ]; then
    echo "Cloning the repository..."
    git clone "$REPO_URL"
fi

# Navigate to the repo directory
cd "$REPO_DIR" || { echo "Directory not found: $REPO_DIR"; exit 1; }

# Pull the latest code
echo "Pulling the latest code from the repository..."
git pull origin main

# Check if the virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
echo "Activating the virtual environment..."
source "$VENV_DIR/bin/activate"

# Install or update dependencies
echo "Installing/updating dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Add the stubs directory to PYTHONPATH
echo "Setting PYTHONPATH..."
export PYTHONPATH=$PYTHONPATH:/home/vadmin/vtpl-grpc-server/stubs


echo "Restarting the gRPC server service..."
sudo systemctl restart grpc_server