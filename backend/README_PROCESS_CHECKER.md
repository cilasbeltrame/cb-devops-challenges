# Container Process Checker

This utility helps diagnose and fix issues with processes not running in challenge containers.

## Problem

A common issue with Docker-based challenges is that background processes mentioned in the challenge description are not actually running when users connect to the container. This can happen for several reasons:

1. The setup script didn't properly start the process in the background
2. The process was started but terminated unexpectedly
3. The process wasn't started with proper persistence mechanisms (nohup, &, etc.)

## Solution

The `container_process_checker.py` script provides tools to:

1. Check if a process is running in a container
2. List all running processes in a container
3. Restart processes that should be running
4. Fix common services like Apache/HTTPD

## Usage

```bash
# Make the script executable
chmod +x backend/container_process_checker.py

# List all running processes in a container
./backend/container_process_checker.py CONTAINER_ID --list

# Check if a specific process is running
./backend/container_process_checker.py CONTAINER_ID --check apache2

# Restart a specific process
./backend/container_process_checker.py CONTAINER_ID --restart "apache2ctl start"

# Fix a common service
./backend/container_process_checker.py CONTAINER_ID --fix apache
```

## Examples

### Example 1: Apache/HTTPD not running

If a challenge mentions an Apache/HTTPD server but it's not running:

```bash
# Check if Apache is running
./backend/container_process_checker.py a213bd5eb22b --check apache2

# If not running, fix it
./backend/container_process_checker.py a213bd5eb22b --fix apache
```

### Example 2: Custom process not running

If a challenge mentions a custom process but it's not running:

```bash
# List all processes to see what's running
./backend/container_process_checker.py b366006061ac --list

# Restart the missing process
./backend/container_process_checker.py b366006061ac --restart "/path/to/process --with args"
```

## Prevention

To prevent this issue in the future, the issue generator has been updated to:

1. Emphasize proper background process handling in the prompt
2. Include specific examples of how to start and verify background processes
3. Add validation checks to ensure setup scripts properly handle background processes

## Troubleshooting

If you encounter issues with the process checker:

1. Make sure you have the correct container ID
2. Try using the full container ID instead of a partial one
3. Ensure the container is running
4. Check if the process is installed in the container 
