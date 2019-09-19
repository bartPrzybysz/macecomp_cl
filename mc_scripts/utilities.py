#
# Utilities for mc_scripts
#

import sys

db_credentials = {'user': '', 'password': '',
                  'host': 'localhost', 'database': 'macecomp'}


def login(driver, username='', password=''):
    """
    Log in to blackboard with the provided webdriver
    """
    driver.get(
        'https://franciscan.blackboard.com/fus.blackboard.com/webapps/login/?action=default_login')
    driver.find_element_by_id('agree_button').click()
    driver.maximize_window()
    driver.find_element_by_id('user_id').send_keys(username)
    driver.find_element_by_id('password').send_keys(password)
    driver.find_element_by_id('entry-login').click()


# credit: https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ... %s\r\r' % (bar, percents, '%', status))
    sys.stdout.flush()
