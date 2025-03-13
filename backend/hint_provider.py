"""
Hint Provider - Generates hints based on the current issue
"""

from typing import Dict, Any, List
import random

# Store hint indices globally
hint_indices = {}

def get_hint(issue: Dict[str, Any]) -> str:
    """
    Get a hint for the current issue.
    
    Args:
        issue: Issue details
        
    Returns:
        Hint string with enumeration (e.g., "Hint 1: Check network connectivity")
    """
    issue_id = issue["id"]
    hints = issue.get("hints", [])
    
    if not hints:
        # Generate a generic hint if no hints are available
        return "Hint 1: " + generate_generic_hint(issue)
    
    # Initialize hint index for this issue if not already done
    if issue_id not in hint_indices:
        hint_indices[issue_id] = 0
    
    # Get the current hint index
    current_index = hint_indices[issue_id]
    
    # Get the hint
    if current_index < len(hints):
        hint = hints[current_index]
        # Increment the hint index for next time
        hint_indices[issue_id] = current_index + 1
        return f"Hint {current_index + 1}: {hint}"
    else:
        # If we've exhausted all hints, either cycle back to the beginning or generate a new one
        if random.random() < 0.7:  # 70% chance to cycle back
            hint_indices[issue_id] = 0
            return f"Hint 1: {hints[0]}"
        else:
            # Generate a more specific hint
            return f"Hint {len(hints) + 1}: {generate_specific_hint(issue)}"

def generate_generic_hint(issue: Dict[str, Any]) -> str:
    """
    Generate a generic hint based on the issue category.
    
    Args:
        issue: Issue details
        
    Returns:
        Generic hint
    """
    category = issue.get("category", "")
    
    generic_hints = {
        "networking": [
            "Check network connectivity with ping or traceroute.",
            "Verify DNS resolution with nslookup or dig.",
            "Check firewall settings with iptables -L.",
            "Examine network interfaces with ip addr or ifconfig."
        ],
        "file_system": [
            "Check disk space with df -h.",
            "Verify file permissions with ls -la.",
            "Look for disk errors with dmesg | grep -i error.",
            "Check mount points with mount or cat /etc/fstab."
        ],
        "process_management": [
            "Check running processes with ps aux.",
            "Look for high CPU usage with top.",
            "Check for zombie processes with ps aux | grep Z.",
            "Examine process details with pstree or htop."
        ],
        "permissions": [
            "Check file ownership with ls -la.",
            "Verify user and group IDs with id.",
            "Look at access control lists with getfacl.",
            "Check sudo permissions with sudo -l."
        ],
        "service_configuration": [
            "Check service status with systemctl status service_name.",
            "Look at service logs with journalctl -u service_name.",
            "Verify configuration files in /etc.",
            "Check for syntax errors in config files."
        ],
        "resource_usage": [
            "Check memory usage with free -m.",
            "Look at disk I/O with iostat.",
            "Monitor system load with uptime.",
            "Check for memory leaks with valgrind."
        ],
        "package_management": [
            "Verify package installation with dpkg -l or rpm -qa.",
            "Check for broken packages with apt --fix-broken install.",
            "Look at package repositories in /etc/apt/sources.list or /etc/yum.repos.d/.",
            "Verify package dependencies with apt-cache depends or yum deplist."
        ]
    }
    
    if category in generic_hints:
        return random.choice(generic_hints[category])
    else:
        return "Try checking system logs in /var/log for error messages."

def generate_specific_hint(issue: Dict[str, Any]) -> str:
    """
    Generate a more specific hint using the solution.
    
    Args:
        issue: Issue details
        
    Returns:
        Specific hint
    """
    solution = issue.get("solution", "")
    
    if not solution:
        return "Look carefully at the error messages and try to understand what they're telling you."
    
    # Extract keywords from the solution
    keywords = [word for word in solution.split() if len(word) > 4]
    
    if not keywords:
        return "The solution involves a common Linux troubleshooting command."
    
    # Pick a random keyword from the solution
    keyword = random.choice(keywords)
    
    return f"The solution involves using or checking something related to '{keyword}'." 
