import argparse
from sys import exit

from mc_scripts import *

ACTIONS = ['terminal', 'upload-transcript']

with open('doc/description.txt') as file:
    description = file.read() 

with open('doc/epilog.txt') as file:
    epilog = file.read()

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
