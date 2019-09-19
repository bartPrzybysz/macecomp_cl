import argparse
from sys import exit

from mc_scripts import *

ACTIONS = ['terminal', 'upload-transcript', 'assign-questions']

description = \
    """Scripts for administrating the MACE COMP system

Actions include the following:
1) upload-transcript
2) assign-questions
"""

epilog = \
    """
1) upload-transcript
    Action for uploading a transcript to the MaceComp database.

    Requires a transcript excel file to be provided that contains the following columns:
        stud_id                 - student id number
        stud_first              - student first name
        stud_last               - student last name
        yr_cde                  - year the student took the class
        trm_cde                 - two digit term code (example: "10")
        crs_cde                 - course number (example: "THE-600")
        transaction_sts         - transaction status character (example: "H")
        crs_div                 - "GT" or "GA"
        instrctr_id             - grading instructor id number
        last_pre_first_middle   - instructor name (example: "Rice, Dr. Robert W.J.")
        instrctr_type           - instructor type character (examples: "P", 8)
        description             - description associated with instructor type (example: "Professor")
        instrctr_fist           - grading instructors first name
        instrctr_last           - grading instructors last name
        pre                     - instructor title (examples: "Dr.", "Prof.")

2) assign-questions
    Action for assigning questions to eligible students
"""

parser = argparse.ArgumentParser(
    description=description, epilog=epilog,
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument('-a', '--action', metavar='Action', type=str,
                    default='terminal', help='Action to be performed',
                    choices=ACTIONS)
parser.add_argument('-f', '--file', metavar='Filepath', type=str,
                    default=None,
                    help='File path of file to be used for specified action')
args = parser.parse_args()

action = args.action

while action == 'terminal':
    action = input('Specify Action: ').lower()

    if action.lower() in {'exit', 'quit', 'stop', 'leave', 'cancel'}:
        exit()

    if action not in ACTIONS:
        print('Unrecognized selection')
        print('The options are ', ACTIONS, '\n')
        action = 'terminal'

if action == 'upload-transcript':
    upload_transcript(args.file)

if action == 'assign-questions':
    assign_questions()
