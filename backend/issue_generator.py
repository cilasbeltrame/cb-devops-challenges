"""
Issue Generator - Integrates with LLM to generate troubleshooting issues
"""

import os
import uuid
import json
import random
from typing import Dict, Any, List, Optional
from openai import OpenAI

# Define categories for different challenge types
CHALLENGE_TYPES = {
    "linux": [
        "networking",
        "file_system",
        "process_management",
        "permissions",
        "service_configuration",
        "resource_usage",
        "package_management"
    ]
}

def validate_issue(issue):
    """
    Validate that an issue has all required fields and valid scripts.
    
    Args:
        issue: Issue to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Check required fields
    required_fields = ["title", "description", "setup_script", "verification_script", "hints", "solution"]
    for field in required_fields:
        if field not in issue or not issue[field]:
            return False
    
    # Check that description is detailed enough
    if len(issue["description"]) < 50:
        return False
    
    # Check that scripts are not empty
    if len(issue["setup_script"]) < 20 or len(issue["verification_script"]) < 20:
        return False
    
    # Check that hints are provided
    if not isinstance(issue["hints"], list) or len(issue["hints"]) < 2:
        return False
    
    return True

def create_issue_prompt(difficulty, category, challenge_type="linux"):
    """
    Create a prompt for the LLM to generate an issue.
    
    Args:
        difficulty: Difficulty level
        category: Issue category
        challenge_type: Type of challenge
        
    Returns:
        Prompt string
    """
    # Base prompt
    prompt = f"""
Create a realistic Linux troubleshooting scenario for a {difficulty} difficulty level in the {category} category.

The scenario should include:
1. A title that briefly describes the issue
2. A detailed description of the problem from the user's perspective
3. A setup script that creates the issue in a Docker container
4. A verification script that checks if the issue has been resolved
5. A list of hints that gradually guide the user to the solution
6. The solution that resolves the issue

The setup script should create a realistic issue that a system administrator might encounter.
The verification script should check if the issue has been resolved and exit with code 0 if successful.

Respond with a JSON object in the following format:
{{
  "id": "unique-id",
  "title": "Brief title of the issue",
  "description": "Detailed description of the problem",
  "category": "{category}",
  "difficulty": "{difficulty}",
  "setup_script": "#!/bin/bash\\n# Script that sets up the issue",
  "verification_script": "#!/bin/bash\\n# Script that verifies the solution",
  "hints": [
    "First hint - general guidance",
    "Second hint - more specific",
    "Third hint - very specific"
  ],
  "solution": "Detailed explanation of the solution",
  "base_image": "ubuntu:20.04"
}}
"""
    
    return prompt

def generate_issue_with_llm(api_key, difficulty, category=None, challenge_type="linux"):
    """
    Generate an issue using LLM.
    
    Args:
        api_key: OpenAI API key
        difficulty: Difficulty level
        category: Optional category
        challenge_type: Type of challenge
        
    Returns:
        Dictionary containing issue details
    """
    # Create a prompt for the LLM
    prompt = create_issue_prompt(difficulty, category, challenge_type)
    
    # Set up the OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Use GPT-4 model
    model = "gpt-4"
    
    try:
        # Make the API call
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a Linux system administrator expert who creates realistic troubleshooting scenarios. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse the response
        content = response.choices[0].message.content
        issue = json.loads(content)
        
        # Ensure the issue has an ID
        if "id" not in issue or not issue["id"]:
            issue["id"] = str(uuid.uuid4())
        
        return issue
    except Exception as e:
        raise ValueError(f"Failed to generate issue with OpenAI: {str(e)}")

def generate_issue(difficulty="medium", category=None, challenge_type="linux", use_predefined=False):
    """
    Generate a troubleshooting issue.
    
    Args:
        difficulty: Difficulty level (easy, medium, hard)
        category: Optional category to filter issues
        challenge_type: Type of challenge (currently only linux)
        use_predefined: Whether to try using predefined scenarios first (ignored, kept for compatibility)
        
    Returns:
        Dictionary containing issue details
    """
    # Get OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    # Set the issue categories based on challenge type
    issue_categories = CHALLENGE_TYPES.get(challenge_type.lower(), CHALLENGE_TYPES["linux"])
    
    # Select a random category if not specified
    if not category:
        category = random.choice(issue_categories)
    
    print(f"Generating issue with LLM...")
    issue = generate_issue_with_llm(api_key, difficulty, category, challenge_type)
    
    # Validate that the issue has all required fields and scripts
    if validate_issue(issue):
        print("Successfully generated issue with LLM.")
        return issue
    else:
        raise ValueError("Generated issue is invalid") 
