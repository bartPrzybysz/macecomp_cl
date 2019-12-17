from time import time
from tkinter import Tk
from tkinter.filedialog import askdirectory
from datetime import date

import pandas as pd

# Relative imports behave differently based on wether this is run as
# a part of the package or as a standalone script
if __name__ == '__main__':
    from utils import progress, bb
else:
    from .utils import progress, bb


Tk().withdraw()  # No need for the full GUI


def count_ungraded(output_dir=None):
    """
    Count ungraded submissions in each COMP org and output results in CSV file.

    Requires a REST API connection
    """
    if not output_dir:
        print('Please specify output location...')
        output_dir = askdirectory(title='Specify output location')

    file_name = f'{output_dir}/UNGRADED_COMPS_{str(date.today())}.csv'

    print(f'\nResults will be saved in {file_name}\n')

    start = time()

    progress(0, 1, "Getting COMP organizations                        ")

    r = bb.GetCourses(params={'name': 'COMP Questions',
                              'organization': True,
                              'fields': 'id,courseId,name,organization'})
    organizations = r.json()['results']

    ungraded_df = pd.DataFrame(data=0, columns=['ungraded'],
                               index=[d['name'] for d in organizations])

    total = len(organizations)

    for i, org in enumerate(organizations):
        progress(i, total, "Getting submissions from organizations    ")

        # Get Gradebook columns
        r = bb.GetGradeColumns(courseId=org['id'],
                               params={'fields': 'id,name'})
        columns = r.json()['results']

        # Filter out the 'total' columns
        columns = [c for c in columns if 'Comp Question' in c['name']]

        for column in columns:
            # Get column submissions
            r = bb.GetColumnAttempts(courseId=org['id'],
                                     columnId=column['id'],
                                     params={
                                         'attemptStatuses': 'NeedsGrading',
                                         'fields': 'id,userId,status'})

            attempts = r.json()['results']

            for attempt in attempts:
                if attempt['status'] == 'NeedsGrading':
                    ungraded_df.loc[org['name'], 'ungraded'] += 1

    ungraded_df.query('ungraded > 0').to_csv(file_name)

    progress(total, total, "All Done                                  ")

    end = time()
    print(f'\n\nProcess took {end - start} seconds\n')


if __name__ == '__main__':
    count_ungraded()
