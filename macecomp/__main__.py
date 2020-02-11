import argparse
from pathlib import Path
import pkg_resources
import json

from . import (assign_questions, upload_transcript, reroll, configure,
               calculate_grades, count_ungraded)

parser = argparse.ArgumentParser(
    description='Tool for managing the MACE COMP system.',
    epilog=pkg_resources.resource_string(
        __name__, 'doc/usage.txt').decode('utf-8'),
    formatter_class=argparse.RawDescriptionHelpFormatter)
subparsers = parser.add_subparsers(title='command')

config_parser = subparsers.add_parser(
    'config',
    description=pkg_resources.resource_string(
        __name__, 'doc/config.txt').decode('utf-8'),
    formatter_class=argparse.RawDescriptionHelpFormatter)
config_parser.set_defaults(command='config')
config_parser.add_argument(
    'file', nargs='?',  default=None,
    help='Name of config file to be used')

upload_transcript_parser = subparsers.add_parser(
    'upload-transcript',
    description=pkg_resources.resource_string(
        __name__, 'doc/upload-transcript.txt').decode('utf-8'),
    formatter_class=argparse.RawDescriptionHelpFormatter)
upload_transcript_parser.set_defaults(command='upload-transcript')
upload_transcript_parser.add_argument(
    'file', nargs='?', default=None,
    help='Name of transcript file')

assign_questions_parser = subparsers.add_parser(
    'assign-questions',
    description=pkg_resources.resource_string(
        __name__, 'doc/assign-questions.txt').decode('utf-8'),
    formatter_class=argparse.RawDescriptionHelpFormatter)
assign_questions_parser.set_defaults(command='assign-questions')

reroll_parser = subparsers.add_parser(
    'reroll',
    description=pkg_resources.resource_string(
        __name__, 'doc/reroll.txt').decode('utf-8'),
    formatter_class=argparse.RawDescriptionHelpFormatter)
reroll_parser.set_defaults(command='reroll')
reroll_parser.add_argument(
    'student_id', nargs='?', default=None, type=int,
    help='A student id')

calculate_grades_parser = subparsers.add_parser(
    'calculate-grades',
    description=pkg_resources.resource_string(
        __name__, 'doc/calculate-grades.txt').decode('utf-8'),
    formatter_class=argparse.RawDescriptionHelpFormatter)
calculate_grades_parser.set_defaults(command='calculate-grades')
calculate_grades_parser.add_argument(
    'output_dir', nargs='?', default=None,
    help='Path to directory where results should be saved')

count_ungraded_parser = subparsers.add_parser(
    'count-ungraded',
    description=pkg_resources.resource_string(
        __name__, 'doc/count-ungraded.txt').decode('utf-8'),
    formatter_class=argparse.RawDescriptionHelpFormatter)
count_ungraded_parser.set_defaults(command='count-ungraded')
count_ungraded_parser.add_argument(
    'output_dir', nargs='?', default=None,
    help='Path to directory where results should be saved')


def main():
    args = parser.parse_args()

    if 'command' not in args:
        print(f"Available commands: {', '.join(subparsers.choices.keys())}")
        args.command = input(f'Please select a command: ')
        args.file = None
        args.student_id = None
        args.output_dir = None

    if args.command == 'config':
        configure(args.file)
    elif args.command == 'upload-transcript':
        upload_transcript(args.file)
    elif args.command == 'assign-questions':
        assign_questions()
    elif args.command == 'reroll':
        reroll(args.student_id)
    elif args.command == 'calculate-grades':
        calculate_grades(args.output_dir)
    elif args.command == 'count-ungraded':
        count_ungraded(args.output_dir)
    else:
        print('Command not found')


if __name__ == '__main__':
    main()
