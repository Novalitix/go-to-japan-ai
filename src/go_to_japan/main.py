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
        print("Début de la mission :", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        resultats = GoToJapan().crew().kickoff(inputs=inputs)
        print("Résultats de la mission :", resultats)
        print("Fin de la mission :", datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

