from time import time
from tkinter import Tk
from tkinter.filedialog import askdirectory
from datetime import date

import pandas as pd

# Relative imports behave differently based on wether this is run as
# a part of the package or as a standalone script
if __name__ == '__main__':
    from utils import progress, bb, db_engine, progress
else:
    from .utils import progress, bb, db_engine, progress


Tk().withdraw()  # No need for the full GUI


def calculate_grades(output_dir=None):
    """
    Create a CSV file with students' grades.

    Requires a database and REST API connection.
    """
    if not output_dir:
        print('Please specify output location...')
        output_dir = askdirectory(title='Specify output location')

    file_name = f'{output_dir}/COMP_GRADES_{str(date.today())}.csv'

    print(f'\nResults will be saved in {file_name}\n')

    start = time()

    all_data = list()

    progress(0, 1, "Getting COMP organizations                        ")

    r = bb.GetCourses(params={'name': 'COMP Questions',
                              'organization': True,
                              'fields': 'id,courseId,name,organization'})
    organizations = r.json()['results']

    total = len(organizations) + 2

    for i, org in enumerate(organizations):
        progress(i, total, "Getting grades from organizations         ")

        # Get Gradebook columns
        r = bb.GetGradeColumns(courseId=org['id'],
                               params={'fields': 'id,name'})
        columns = r.json()['results']

        # Filter out the 'total' columns
        columns = [c for c in columns if 'Comp Question' in c['name']]

        for column in columns:
            # Get Column Grades
            r = bb.GetColumnGrades(courseId=org['id'],
                                   columnId=column['id'],
                                   params={'fields': 'userId,displayGrade'})
            grades = r.json()['results']

            for grade in grades:
                # Get user information
                r = bb.GetUser(userId=grade['userId'],
                               params={'fields': 'name,studentId'})
                user = r.json()

                name = f"{user['name']['given']} {user['name']['family']}"

                numeric_grade = grade['displayGrade']['score'] \
                    if 'displayGrade' in grade else None

                # Add a dict to all_data
                all_data.append({
                    'student_id': user['studentId'],
                    'name': name,
                    'organization': org['name'],
                    'comp_id': int(column['name'].split()[-1]),
                    'grade': numeric_grade
                })

    # Create a dataframe out of all_data
    data_df = pd.DataFrame(all_data)
    data_df.student_id = data_df.student_id.astype('int64')

    progress(total-2, total, "Getting question assignments            ")

    # Fetch the 4Q table from the database
    fourq_df = pd.read_sql_table('4q', db_engine, index_col='student_id')

    progress(total-1, total, "Calculating grade totals                ")

    # Merge 4Q to grade data
    merge_df = data_df.merge(fourq_df,
                             left_on='student_id',
                             right_on='student_id')

    # Filter out submissions to unassigned questions
    merge_df = merge_df.query(("comp_id == Q1 or comp_id == Q2 "
                               "or comp_id == Q3 or comp_id == Q4"))

    # Format for output
    result_df = pd.DataFrame(columns=['student_id', 'name', 'grade_1',
                                      'grade_2', 'grade_3', 'grade_4',
                                      'total']).set_index('student_id')

    # Iterate over each students entries
    for student_id, grades in merge_df.groupby('student_id'):
        result_df.loc[student_id, 'name'] = grades.name.iloc[0]

        # Make sure list of grades has four entries and add it to result
        g = list(grades.grade.values)
        g += [float('nan')] * (4 - len(g))
        result_df.loc[student_id, 'grade_1':'grade_4'] = g

        result_df.loc[student_id, 'total'] = sum(g)

    result_df.to_csv(file_name)

    progress(total, total, "All Done                                  ")

    end = time()
    print(f'\n\nProcess took {end - start} seconds\n')


if __name__ == '__main__':
    calculate_grades()
