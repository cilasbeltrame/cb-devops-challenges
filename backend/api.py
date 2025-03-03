#!/usr/bin/env python3
"""
API for Linux Troubleshooting Simulator
"""

import os
import uuid
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import container_manager
import issue_generator
import solution_verifier
import hint_provider
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store active containers and issues
active_sessions = {}

@app.route('/api/generate-issue', methods=['POST'])
def generate_issue():
    """Generate a new issue and create a container for it."""
    try:
        data = request.json
        difficulty = data.get('difficulty', 'medium')
        
        # Generate a new issue
        issue = issue_generator.generate_issue(difficulty, challenge_type="linux", use_predefined=True)
        
        # Create a container for the issue
        container_id = container_manager.create_container(issue)
        
        # Store the issue and container ID
        session_id = str(uuid.uuid4())
        active_sessions[session_id] = {
            'issue': issue,
            'container_id': container_id
        }
        
        # Return the issue details and session ID
        return jsonify({
            'success': True,
            'id': session_id,
            'title': issue['title'],
            'description': issue['description'],
            'difficulty': difficulty,
            'containerId': container_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/execute-command', methods=['POST'])
def execute_command():
    """Execute a command in the container."""
    try:
        data = request.json
        container_id = data.get('containerId')
        command = data.get('command')
        
        if not container_id or not command:
            return jsonify({
                'success': False,
                'error': 'Container ID and command are required'
            }), 400
        
        # Execute the command in the container
        output = container_manager.execute_command(container_id, command)
        
        return jsonify({
            'success': True,
            'output': output
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'output': f"Error: {str(e)}"
        }), 500

@app.route('/api/verify-solution', methods=['POST'])
def verify_solution():
    """Verify if the issue has been resolved."""
    try:
        data = request.json
        session_id = data.get('sessionId')
        
        if not session_id or session_id not in active_sessions:
            return jsonify({
                'success': False,
                'error': 'Invalid session ID'
            }), 400
        
        container_id = active_sessions[session_id]['container_id']
        issue = active_sessions[session_id]['issue']
        
        # Verify the solution
        result, feedback = solution_verifier.verify_solution(container_id, issue)
        
        return jsonify({
            'success': result,
            'message': feedback
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f"Error: {str(e)}"
        }), 500

@app.route('/api/get-hint', methods=['POST'])
def get_hint():
    """Get a hint for the current issue."""
    try:
        data = request.json
        session_id = data.get('sessionId')
        
        if not session_id or session_id not in active_sessions:
            return jsonify({
                'success': False,
                'error': 'Invalid session ID'
            }), 400
        
        issue = active_sessions[session_id]['issue']
        
        # Get a hint using the hint provider's enumeration system
        hint = hint_provider.get_hint(issue)
        
        return jsonify({
            'success': True,
            'hint': hint
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'hint': f"Error: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 
