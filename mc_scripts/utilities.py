#
# Utilities for mc_scripts
#

import sys
import json

# Change the path to point to the proper config file
with open('macecomp_config.json', 'r') as config_file:
    CONFIG = json.load(config_file)


# credit: https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ... %s\r\r' % (bar, percents, '%', status))
    sys.stdout.flush()
