#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from go_to_japan.crew import GoToJapan

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information



def run():

    inputs = {
        'planningType': 'explore',
        'travelWith': 'solo',
        'pace': 'equilibre',
        'firstName': 'Yann',
        'departureDate': '2025-10-11',
        'returnDate': '2025-10-13',
        'duration': '2',
        'departurePeriod': [],
        'citiesToInclude': ['Kyoto'],
        'citiesToExclude': [],
        'budget': '5000',
        'comments': '',
        'interests': [
            'temples'
        ],
        'services': [
            'restaurants',
            'lodging',
        ],
    }
    """
    Run the crew.
    """
    
    try:
        GoToJapan().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'planningType': 'explore',
        'travelWith': 'solo',
        'pace': 'equilibre',
        'firstName': 'Yann',
        'departureDate': '2025-10-11',
        'returnDate': '2025-10-13',
        'duration': '2',
        'departurePeriod': [],
        'citiesToInclude': ['Kyoto'],
        'citiesToExclude': [],
        'budget': '5000',
        'comments': '',
        'interests': [
            'temples'
        ],
        'services': [
            'restaurants',
            'lodging',
        ],
    }
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

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'planningType': 'explore',
        'travelWith': 'solo',
        'pace': 'equilibre',
        'firstName': 'Yann',
        'departureDate': '2025-10-11',
        'returnDate': '2025-10-13',
        'duration': '2',
        'departurePeriod': [],
        'citiesToInclude': ['Kyoto'],
        'citiesToExclude': [],
        'budget': '5000',
        'comments': '',
        'interests': [
            'temples'
        ],
        'services': [
            'restaurants',
            'lodging',
        ],
    }

    
    try:
        GoToJapan().crew().test(n_iterations=1, eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
