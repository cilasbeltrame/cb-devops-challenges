#!/usr/bin/env python3
"""
Linux Troubleshooting Simulator - Main Application
"""

import os
import sys
import typer
import random
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from dotenv import load_dotenv

import container_manager
import issue_generator
import solution_verifier
import hint_provider

# Load environment variables
load_dotenv()

app = typer.Typer()
console = Console()

def check_requirements():
    """Check if all requirements are met to run the application."""
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]Error:[/bold red] OPENAI_API_KEY environment variable is not set.")
        return False
    
    return True

@app.command()
def start(
    difficulty: str = typer.Option("medium", help="Difficulty level: easy, medium, hard"),
    debug: bool = typer.Option(False, help="Enable debug mode for detailed error information")
):
    """Start the Linux Troubleshooting Simulator."""
    if not check_requirements():
        sys.exit(1)
    
    console.print(Panel.fit(
        "[bold green]Linux Troubleshooting Simulator[/bold green]\n\n"
        "Welcome! This application will generate real Linux issues in containers,\n"
        "provide hints when requested, and verify your solutions.",
        title="Welcome",
        border_style="green"
    ))
    
    # Check if Docker is running
    container_manager.check_docker()
    
    # Generate a new issue (Linux only for now)
    try:
        issue = issue_generator.generate_issue(difficulty, challenge_type="linux", use_predefined=False)
    except Exception as e:
        if debug:
            import traceback
            console.print("[bold red]Debug Traceback:[/bold red]")
            console.print(traceback.format_exc())
            
        console.print(Panel.fit(
            f"[bold red]Error:[/bold red] Failed to generate issue with OpenAI.\n\n"
            f"Error details: {str(e)}\n\n"
            "Please check the following:\n"
            "1. Your OpenAI API key is correct and has sufficient credits\n"
            "2. You have access to the GPT-4 model\n"
            "3. Your internet connection is working\n"
            "4. The OpenAI API is not experiencing downtime\n\n"
            "Try running with --debug flag for more detailed error information.",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)
    
    # Create container with the issue
    container_id = container_manager.create_container(issue)
    
    try:
        # Display task instructions
        console.print(f"\n[bold]Challenge:[/bold] {issue['title']}")
        console.print(f"\n[bold]Description:[/bold] {issue['description']}")
        
        # Display detailed instructions
        console.print("\n[bold]Instructions:[/bold]")
        console.print(Markdown("""
1. Connect to the container using the command below
2. Investigate the issue using standard Linux troubleshooting techniques
3. Apply the necessary fix
4. Select 'verify' to check if your solution is correct
5. If you're stuck, select 'hint' for guidance
        """))
        
        console.print(f"\n[bold]Container ID:[/bold] {container_id}")
        console.print("\nConnect to the container using:")
        console.print(f"[bold]docker exec -it {container_id} bash[/bold]")
        
        while True:
            action = Prompt.ask(
                "\nWhat would you like to do?",
                choices=["hint", "verify", "quit"],
                default="verify"
            )
            
            if action == "hint":
                hint = hint_provider.get_hint(issue)
                console.print(f"\n[bold]Hint:[/bold] {hint}")
            
            elif action == "verify":
                result, feedback = solution_verifier.verify_solution(container_id, issue)
                if result:
                    console.print(Panel.fit(
                        "[bold green]Congratulations![/bold green]\n\n"
                        f"{feedback}",
                        title="Success",
                        border_style="green"
                    ))
                    
                    if Confirm.ask("Would you like to try another challenge?"):
                        # Clean up the current container
                        container_manager.remove_container(container_id)
                        
                        # Generate a new issue with LLM
                        try:
                            issue = issue_generator.generate_issue(difficulty, challenge_type="linux", use_predefined=False)
                        except Exception as e:
                            console.print(Panel.fit(
                                f"[bold red]Error:[/bold red] Failed to generate a new issue with OpenAI.\n\n"
                                f"Error details: {str(e)}\n\n"
                                "Please check the following:\n"
                                "1. Your OpenAI API key is correct and has sufficient credits\n"
                                "2. You have access to the GPT-4 model\n"
                                "3. Your internet connection is working\n"
                                "4. The OpenAI API is not experiencing downtime\n\n"
                                "Try running with --debug flag for more detailed error information.",
                                title="Error",
                                border_style="red"
                            ))
                            sys.exit(1)
                        
                        # Create container with the issue
                        container_id = container_manager.create_container(issue)
                        
                        console.print(f"\n[bold]New Challenge:[/bold] {issue['title']}")
                        console.print(f"\n[bold]Description:[/bold] {issue['description']}")
                        
                        # Display detailed instructions again
                        console.print("\n[bold]Instructions:[/bold]")
                        console.print(Markdown("""
1. Connect to the container using the command below
2. Investigate the issue using standard Linux troubleshooting techniques
3. Apply the necessary fix
4. Select 'verify' to check if your solution is correct
5. If you're stuck, select 'hint' for guidance
                        """))
                        
                        console.print(f"\n[bold]Container ID:[/bold] {container_id}")
                        console.print("\nConnect to the container using:")
                        console.print(f"[bold]docker exec -it {container_id} bash[/bold]")
                    else:
                        # Clean up the container before exiting
                        container_manager.remove_container(container_id)
                        console.print("Thank you for using the Linux Troubleshooting Simulator!")
                        break
                else:
                    console.print(Panel.fit(
                        "[bold red]Not quite right yet.[/bold red]\n\n"
                        f"{feedback}",
                        title="Try Again",
                        border_style="red"
                    ))
            
            elif action == "quit":
                # Clean up the container
                container_manager.remove_container(container_id)
                console.print("Thank you for using the Linux Troubleshooting Simulator!")
                break
    except KeyboardInterrupt:
        # Ensure container cleanup on keyboard interrupt
        console.print("\nExiting the simulator...")
        container_manager.remove_container(container_id)

# Set the start command as the default command
@app.callback()
def callback():
    """Linux Troubleshooting Simulator - An interactive application for practicing Linux troubleshooting skills."""
    pass

if __name__ == "__main__":
    app() 
