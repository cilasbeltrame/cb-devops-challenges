"""
Container Manager - Handles Docker container creation and management
"""

import os
import sys
import subprocess
import tempfile
import json
from typing import Dict, Any, Optional, Tuple

def check_docker():
    """Check if Docker is installed and running."""
    try:
        # Check if Docker is installed and running using subprocess
        result = subprocess.run(["docker", "info"], capture_output=True, text=True, check=True)
        if result.returncode != 0:
            raise Exception("Docker is not running")
    except Exception as e:
        print(f"Error connecting to Docker: {e}")
        print("Please ensure Docker is installed and running.")
        sys.exit(1)

def create_container(issue: Dict[str, Any]) -> str:
    """
    Create a Docker container with the specified issue.
    
    Args:
        issue: Dictionary containing issue details
        
    Returns:
        Container ID
    """
    try:
        # Create a temporary directory to store setup scripts
        temp_dir = tempfile.mkdtemp()
        
        # Create setup script
        setup_script_path = os.path.join(temp_dir, "setup.sh")
        with open(setup_script_path, "w") as f:
            f.write(issue["setup_script"])
        os.chmod(setup_script_path, 0o755)
        
        # Create Dockerfile
        dockerfile_path = os.path.join(temp_dir, "Dockerfile")
        with open(dockerfile_path, "w") as f:
            f.write(f"""
FROM {issue.get('base_image', 'ubuntu:20.04')}

# Install basic utilities
RUN apt-get update && apt-get install -y \\
    curl \\
    wget \\
    vim \\
    nano \\
    less \\
    procps \\
    net-tools \\
    iputils-ping \\
    dnsutils \\
    iproute2 \\
    man-db \\
    && rm -rf /var/lib/apt/lists/*

# Copy setup script
COPY setup.sh /tmp/setup.sh

# Run setup script to create the issue
RUN /tmp/setup.sh && rm /tmp/setup.sh

# Set working directory
WORKDIR /root

# Keep container running
CMD ["tail", "-f", "/dev/null"]
""")
        
        # Build the Docker image using subprocess
        print("Building Docker image... (this may take a few minutes)")
        image_tag = f"linux-troubleshooting-{issue['id'].lower()}"
        
        subprocess.run(["docker", "build", "-t", image_tag, temp_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print("Docker image built successfully.")
        # Create and start the container using subprocess
        print("Creating and starting container...")
        container_name = f"linux-issue-{issue['id'].lower()}"
        result = subprocess.run(
            ["docker", "run", "-d", "--name", container_name, "-t", image_tag],
            capture_output=True, text=True, check=True
        )
        container_id = result.stdout.strip()
        
        return container_id
        
    except subprocess.CalledProcessError as e:
        print(f"Error creating container: {e}")
        print("Please ensure Docker is installed and running.")
        sys.exit(1)

def remove_container(container_id: str) -> None:
    """
    Remove a Docker container.
    
    Args:
        container_id: ID of the container to remove
    """
    try:
        # Stop the container
        subprocess.run(["docker", "stop", container_id], check=False)
        
        # Remove the container
        subprocess.run(["docker", "rm", container_id], check=False)
        
    except subprocess.CalledProcessError as e:
        print(f"Error removing container: {e}")

def execute_command(container_id: str, command: str) -> str:
    """
    Execute a command in the container.
    
    Args:
        container_id: ID of the container
        command: Command to execute
        
    Returns:
        Command output
    """
    try:
        result = subprocess.run(
            ["docker", "exec", container_id] + command.split(),
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command in container: {e}")
        return f"Error: {e}"

def get_container_status(container_id: str) -> Optional[Dict[str, Any]]:
    """
    Get container status information.
    
    Args:
        container_id: ID of the container
        
    Returns:
        Container status information or None if container not found
    """
    try:
        result = subprocess.run(
            ["docker", "inspect", container_id],
            capture_output=True, text=True, check=True
        )
        container_info = json.loads(result.stdout)[0]
        
        return {
            'id': container_info['Id'],
            'status': container_info['State']['Status'],
            'name': container_info['Name'].lstrip('/'),
            'image': container_info['Config']['Image']
        }
    except subprocess.CalledProcessError:
        return None
    except Exception as e:
        print(f"Error getting container status: {e}")
        return None 
