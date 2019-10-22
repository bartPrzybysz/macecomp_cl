'''
Utilities for mc_scripts
'''

import sys
import json
from pathlib import Path
from pprint import pprint

from sqlalchemy import create_engine

with open(f'{Path.home()}/macecomp_config.json') as file:
    CONFIG = json.load(file)


# Connect to database
db_engine = create_engine(
    'mysql+mysqlconnector://{user}:{password}@{host}/{database}'.
    format(**CONFIG['DATABASE'])
)


def configure(file_path=None):
    if not file_path:
        pprint(CONFIG)
        return
    
    with open(file_path) as new_config_file, \
         open(f'{Path.home()}/macecomp_config.json', 'w+') as config_file:
        json.dump(json.load(new_config_file), config_file, indent=4)


# credit: https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ... %s\r\r' % (bar, percents, '%', status))
    sys.stdout.flush()
