#!/usr/bin/env python3
"""
Container Process Checker

This utility helps diagnose and fix issues with processes not running in challenge containers.
It can be used to:
1. Check if a process mentioned in a challenge is actually running
2. Restart processes that should be running but aren't
3. Fix common issues with process persistence in containers
"""

import subprocess
import json
import argparse
import os
import sys

def get_container_id(container_name_or_id):
    """Get the full container ID from a partial ID or name"""
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{.ID}}"],
            capture_output=True, text=True, check=True
        )
        container_ids = result.stdout.strip().split('\n')
        matching_ids = [cid for cid in container_ids if cid.startswith(container_name_or_id)]
        
        if not matching_ids:
            print(f"No container found matching ID or name: {container_name_or_id}")
            return None
        
        if len(matching_ids) > 1:
            print(f"Multiple containers found matching: {container_name_or_id}")
            print("Please provide a more specific ID")
            return None
            
        return matching_ids[0]
    except subprocess.CalledProcessError as e:
        print(f"Error getting container ID: {e}")
        return None

def check_process_in_container(container_id, process_name):
    """Check if a process is running in the container"""
    try:
        result = subprocess.run(
            ["docker", "exec", container_id, "ps", "aux"],
            capture_output=True, text=True, check=True
        )
        return process_name in result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error checking process in container: {e}")
        return False

def restart_process_in_container(container_id, process_command, use_nohup=True):
    """Restart a process in the container"""
    try:
        cmd = ["docker", "exec", container_id, "bash", "-c"]
        
        if use_nohup:
            full_cmd = f"nohup {process_command} > /dev/null 2>&1 &"
        else:
            full_cmd = f"{process_command} &"
            
        cmd.append(full_cmd)
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Verify the process started
        if check_process_in_container(container_id, process_command.split()[0]):
            print(f"Successfully started process: {process_command}")
            return True
        else:
            print(f"Failed to start process: {process_command}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error restarting process in container: {e}")
        return False

def list_running_processes(container_id):
    """List all running processes in the container"""
    try:
        result = subprocess.run(
            ["docker", "exec", container_id, "ps", "aux"],
            capture_output=True, text=True, check=True
        )
        print("Running processes in container:")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error listing processes in container: {e}")
        return False

def fix_apache_in_container(container_id):
    """Fix Apache/HTTPD service in container"""
    try:
        # Check if apache2 or httpd is installed
        apache_check = subprocess.run(
            ["docker", "exec", container_id, "bash", "-c", "command -v apache2 || command -v httpd"],
            capture_output=True, text=True
        )
        
        apache_cmd = apache_check.stdout.strip()
        if not apache_cmd:
            print("Apache/HTTPD not found in container")
            return False
            
        # Determine if it's apache2 or httpd
        is_apache2 = "apache2" in apache_cmd
        
        # Start the service
        if is_apache2:
            start_cmd = "apache2ctl start"
        else:
            start_cmd = "httpd"
            
        print(f"Starting {apache_cmd}...")
        subprocess.run(
            ["docker", "exec", container_id, "bash", "-c", start_cmd],
            capture_output=True, text=True
        )
        
        # Verify it's running
        if is_apache2:
            check_process = "apache2"
        else:
            check_process = "httpd"
            
        if check_process_in_container(container_id, check_process):
            print(f"Successfully started {check_process}")
            return True
        else:
            print(f"Failed to start {check_process}")
            return False
    except Exception as e:
        print(f"Error fixing Apache in container: {e}")
        return False

def fix_common_services(container_id, service_name):
    """Fix common services in container"""
    service_map = {
        "apache": fix_apache_in_container,
        "httpd": fix_apache_in_container,
        "apache2": fix_apache_in_container,
    }
    
    if service_name.lower() in service_map:
        return service_map[service_name.lower()](container_id)
    else:
        print(f"No automatic fix available for service: {service_name}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Check and fix processes in challenge containers")
    parser.add_argument("container_id", help="Container ID or name")
    parser.add_argument("--check", help="Check if a specific process is running")
    parser.add_argument("--restart", help="Restart a specific process")
    parser.add_argument("--list", action="store_true", help="List all running processes")
    parser.add_argument("--no-nohup", action="store_true", help="Don't use nohup when restarting processes")
    parser.add_argument("--fix", help="Fix a common service (apache, httpd, etc.)")
    
    args = parser.parse_args()
    
    # Get full container ID
    container_id = get_container_id(args.container_id)
    if not container_id:
        sys.exit(1)
    
    # List all processes
    if args.list:
        list_running_processes(container_id)
        
    # Check specific process
    if args.check:
        if check_process_in_container(container_id, args.check):
            print(f"Process '{args.check}' is running in the container")
        else:
            print(f"Process '{args.check}' is NOT running in the container")
            
    # Restart specific process
    if args.restart:
        restart_process_in_container(container_id, args.restart, not args.no_nohup)
        
    # Fix common service
    if args.fix:
        fix_common_services(container_id, args.fix)
        
if __name__ == "__main__":
    main() 
