# Linux Troubleshooting Simulator

An interactive application that generates real Linux issues in containers, provides hints, and verifies solutions.

## Features

- Generates realistic Linux issues using LLM integration
- Runs issues in isolated Docker containers
- Provides hints when requested
- Verifies if the user's solution correctly resolves the issue
- Tracks user progress and learning

## Requirements

- Python 3.9+
- Docker
- OpenAI API key (or other LLM provider)

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd linux-troubleshooting-simulator
   ```

2. Run the setup script (recommended):
   ```
   python setup.py
   ```
   This script will:
   - Check if Python 3.9+ is installed
   - Install required dependencies
   - Help you set up your OpenAI API key

   Alternatively, you can install dependencies manually:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

   **Note:** If you encounter installation issues related to Rust compiler requirements, you have two options:
   
   - Option 1: Install Rust using rustup:
     ```
     curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
     source "$HOME/.cargo/env"
     pip install -r requirements.txt
     ```
   
   - Option 2: We've configured the requirements.txt to use an older version of pydantic that doesn't require Rust compilation, which should work for most users.

3. Set up your environment variables (if not done via setup.py):
   Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
   
   Alternatively, you can export it directly:
   ```
   export OPENAI_API_KEY=your_api_key_here
   ```

## Step-by-Step User Guide

### Starting the Application

1. Ensure Docker is running on your system before starting the application.

2. Start the application:
   ```
   python main.py
   ```
   
   You can specify a difficulty level:
   ```
   python main.py start --difficulty easy
   ```
   Options are: easy, medium (default), hard

3. The application will check requirements and generate a Linux issue.

4. You'll see:
   - Challenge title
   - Description of the issue
   - Container ID
   - Command to connect to the container

### Solving a Challenge

1. **Connect to the Container**:
   Open a new terminal window and run the provided command:
   ```
   docker exec -it <container-id> bash
   ```

2. **Investigate the Issue**:
   Use Linux commands to diagnose and troubleshoot the problem.
   
3. **Request Hints** (if needed):
   - In the main application window (not the container terminal), you'll see a prompt asking "What would you like to do?"
   - Type `hint` and press Enter
   - The application will display a hint to help you solve the issue
   - Each time you request a hint, you'll receive progressively more specific guidance

4. **Apply a Solution**:
   Based on your investigation and any hints, implement a solution in the container.

5. **Verify Your Solution**:
   - In the main application window, when prompted for an action, type `verify`
   - The application will check if your solution resolves the issue
   - You'll receive feedback on whether your solution was successful

6. **Next Steps**:
   - If successful: You can choose to try another challenge or exit
   - If unsuccessful: Continue troubleshooting and try again

7. **Exit the Application**:
   Type `quit` when prompted for an action to clean up containers and exit.

### Example Walkthrough: DNS Resolution Issue

1. Start the application and connect to the container.

2. Inside the container, try to ping a domain:
   ```
   ping google.com
   ```
   You'll see an error about unknown host.

3. Check if you can ping an IP address:
   ```
   ping 8.8.8.8
   ```
   This should work, indicating a DNS issue.

4. Examine the DNS configuration:
   ```
   cat /etc/resolv.conf
   ```
   You'll see it's empty or has only comments.

5. Try to modify the file:
   ```
   echo "nameserver 8.8.8.8" > /etc/resolv.conf
   ```
   This will fail because the file is immutable.

6. Request a hint from the main application:
   - In the main application window, type `hint` when prompted
   - You might receive a hint like: "Check the DNS configuration files in the system."
   - Request another hint if needed: "Look at the contents of /etc/resolv.conf file."
   - And another if still stuck: "If you can't modify /etc/resolv.conf directly, check if it has special attributes with 'lsattr /etc/resolv.conf'."

7. Check file attributes:
   ```
   lsattr /etc/resolv.conf
   ```
   You'll see it has the immutable attribute.

8. Remove the immutable attribute:
   ```
   chattr -i /etc/resolv.conf
   ```

9. Add a nameserver:
   ```
   echo "nameserver 8.8.8.8" > /etc/resolv.conf
   ```

10. Verify your solution:
    - In the main application window, type `verify`
    - You'll receive a success message with an explanation of the solution

### Additional Commands

- **List Available Scenarios**:
  ```
  python main.py list-scenarios
  ```
  This will show all predefined scenarios available in the application.

## Project Structure

- `main.py`: Entry point for the application
- `container_manager.py`: Handles Docker container creation and management
- `issue_generator.py`: Integrates with LLM to generate Linux issues
- `solution_verifier.py`: Checks if the user's solution resolves the issue
- `hint_provider.py`: Generates hints based on the current issue
- `scenarios/`: Directory containing predefined issue scenarios
- `templates/`: Docker templates for different Linux environments
- `utils/`: Utility functions and helpers

## License

MIT 
