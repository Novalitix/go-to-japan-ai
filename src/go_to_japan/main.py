#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from go_to_japan.crew import GoToJapan

from typing import Dict, Any

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information



def run(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the crew.
    """
    
    try:
        result = GoToJapan().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Train the crew for a given number of iterations.
    """
    try:
        GoToJapan().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        GoToJapan().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test(inputs: Dict[str, Any]) -> Dict[str, Any]:   
    """
    Test the crew execution and returns the results.
    """
    
    try:
        GoToJapan().crew().test(n_iterations=1, eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
