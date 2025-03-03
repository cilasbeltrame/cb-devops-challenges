"""
Solution Verifier - Checks if the user's solution resolves the issue
"""

import tempfile
import os
import subprocess
from typing import Dict, Any, Tuple

def verify_solution(container_id: str, issue: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Verify if the user's solution resolves the issue.
    
    Args:
        container_id: ID of the container
        issue: Issue details
        
    Returns:
        Tuple of (success, feedback)
    """
    # Create a temporary file for the verification script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(issue["verification_script"])
        verification_script_path = f.name
    print(f"Verification script path: {verification_script_path}")
    try:
        # Make the script executable
        os.chmod(verification_script_path, 0o755)
        
        # Create a temporary directory in the container
        subprocess.run(["docker", "exec", container_id, "mkdir", "-p", "/tmp"], check=True)
        
        # Copy the verification script to the container
        subprocess.run(["docker", "cp", verification_script_path, f"{container_id}:/tmp/verification_script.sh"], check=True)
        
        # Make sure the script is executable in the container
        subprocess.run(["docker", "exec", container_id, "chmod", "+x", "/tmp/verification_script.sh"], check=True)
        
        # Run the verification script and get the exit code
        exit_code_result = subprocess.run(
            ["docker", "exec", container_id, "bash", "-c", "bash /tmp/verification_script.sh; echo $?"],
            capture_output=True, text=True, check=True
        )
        
        # Get the output and exit code
        output = exit_code_result.stdout.strip()
        lines = output.splitlines()
        exit_code = int(lines[-1]) if lines else 1  # Default to 1 (error) if no output
        
        # Remove the exit code from the output
        result = '\n'.join(lines[:-1]) if len(lines) > 1 else ""
        
        # Check if the issue is resolved
        if exit_code == 0:
            return True, generate_success_feedback(issue)
        else:
            return False, generate_failure_feedback(issue, result)
    finally:
        # Clean up
        pass
        # os.unlink(verification_script_path)
        # subprocess.run(["docker", "exec", container_id, "rm", "-f", "/tmp/verification_script.sh"], check=False)

def generate_success_feedback(issue: Dict[str, Any]) -> str:
    """
    Generate feedback for a successful solution.
    
    Args:
        issue: Issue details
        
    Returns:
        Success feedback
    """
    return f"""
Great job! You've successfully resolved the issue: {issue['title']}

The solution was:
{issue['solution']}

This is a common issue in {issue['category']} scenarios. Understanding how to troubleshoot and fix this type of problem is valuable for system administration and DevOps roles.
"""

def generate_failure_feedback(issue: Dict[str, Any], result: str) -> str:
    """
    Generate feedback for a failed solution attempt.
    
    Args:
        issue: Issue details
        result: Output from verification script
        
    Returns:
        Failure feedback
    """
    return f"""
The issue hasn't been completely resolved yet. Keep trying!

Verification output:
{result}

Remember, you can ask for a hint if you're stuck.
""" 
