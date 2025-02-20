#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from instaagent.crew import Instaagent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def load_user_preferences() -> dict:
    """
    Load user preferences from knowledge/user_preference.txt
    Returns a dictionary of preferences with nested sections.
    """
    preferences = {}
    try:
        with open("knowledge/user_preference.txt", "r") as f:
            current_section = None
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                # Check if this is a section header
                if line.startswith("##"):
                    current_section = line.strip("# ").lower().replace(" ", "_")
                    # Initialize the section as an empty dictionary
                    preferences[current_section] = {}
                    continue
                
                # Process key-value pairs
                if ":" in line and current_section:
                    key, value = line.split(":", 1)
                    key = key.strip().lower().replace(" ", "_")
                    value = value.strip()
                    # Add the key-value pair to the current section
                    preferences[current_section][key] = value
    except FileNotFoundError:
        print("Warning: User preferences file not found. Using default settings.")
    
    return preferences

def run() -> None:
    """
    Run the crew.

    This function is responsible for loading user preferences and
    preparing the inputs for the crew. It then kicks off the crew
    with the provided inputs.
    """
    # Load user preferences from the file knowledge/user_preference.txt
    preferences = load_user_preferences()
    
    # Extract key information from the user preferences
    content_topics = preferences.get('content_preferences', {}).get('content_topics', 'AI, tech')
    hashtags = preferences.get('monitoring_preferences', {}).get('hashtags_to_monitor', '')
    accounts = preferences.get('monitoring_preferences', {}).get('accounts_to_monitor', '')
    
    # Prepare inputs for the crew
    inputs = {
        'topic': content_topics.split(',')[0].strip(),  # Use first topic as default
        'current_year': str(datetime.now().year),
        'hashtags_to_monitor': hashtags,
        'accounts_to_monitor': accounts,
        'content_preferences': preferences.get('content_preferences', {})
    }
    
    try:
        # Kick off the crew
        Instaagent().crew().kickoff(inputs=inputs)
    except Exception as e:
        # Handle any exceptions raised during the execution of the crew
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.

    This function is used to train the crew with a given topic. The training
    process is done by running the crew's `train` method with the given inputs.

    Parameters
    ----------
    n_iterations : int
        The number of iterations to train the crew.
    filename : str
        The filename to save the training results.
    inputs : dict
        The inputs to the crew, including the topic to train with.

    Raises
    ------
    Exception
        If an error occurs while training the crew.
    """
    # Load user preferences
    preferences = load_user_preferences()
    content_topics = preferences.get('content_preferences', {}).get('content_topics', 'AI, tech')
    
    inputs = {
        "topic": content_topics.split(',')[0].strip()  # Use first topic as default
    }
    
    try:
        Instaagent().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.

    This function replays the execution of the CrewAI from a specified task ID
    passed as a command-line argument. It handles exceptions that may occur
    during the replay process and raises an appropriate error message.
    """
    try:
        # Replay the crew with the given task ID from command-line arguments
        Instaagent().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        # Raise an exception with an error message if replay fails
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.

    This function is used to test the crew for a given number of iterations.
    It takes two command-line arguments: the number of iterations to test and
    the OpenAI model name to use for testing.

    Parameters
    ----------
    n_iterations : int
        The number of iterations to test the crew.
    openai_model_name : str
        The name of the OpenAI model to use for testing.

    Returns
    -------
    results : dict
        The results of the testing process.

    Raises
    ------
    Exception
        If an error occurs while testing the crew.
    """
    # Load user preferences
    preferences = load_user_preferences()
    content_topics = preferences.get('content_preferences', {}).get('content_topics', 'AI, tech')

    # Set up the inputs to the crew
    inputs = {
        "topic": content_topics.split(',')[0].strip()  # Use first topic as default
    }

    try:
        # Test the crew with the given inputs
        results = Instaagent().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)
        return results
    except Exception as e:
        # Raise an exception with an error message if testing fails
        raise Exception(f"An error occurred while testing the crew: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m instaagent.main [run|train|replay|test] [args]")
        sys.exit(1)
        
    command = sys.argv[1].lower()
    sys.argv = sys.argv[1:]  # Remove the first argument
    
    if command == "run":
        run()
    elif command == "train" and len(sys.argv) >= 2:
        train()
    elif command == "replay" and len(sys.argv) >= 1:
        replay()
    elif command == "test" and len(sys.argv) >= 2:
        test()
    else:
        print("Invalid command or missing arguments")
        print("Usage: python -m instaagent.main [run|train|replay|test] [args]")
        sys.exit(1)