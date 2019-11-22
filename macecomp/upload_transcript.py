from tkinter import Tk
from tkinter.filedialog import askopenfilename
from time import time
import warnings

import pandas as pd

# Relative imports behave differently based on wether this is run as
# a part of the package or as a standalone script
if __name__ == '__main__':
    from utils import progress, db_engine
else:
    from .utils import progress, db_engine


Tk().withdraw()  # No need for the full GUI

# Ignore setting with copy warning
warnings.simplefilter(action='ignore')

# SQL snippet for setting priority status of a class
priority_sql = """
UPDATE CLASS SET priority=1;
UPDATE CLASS SET priority=2
WHERE crs_cde LIKE 'THE-600%'
OR crs_cde LIKE 'THE-618%'
OR crs_cde LIKE 'THE-612%'
OR crs_cde LIKE 'THE-606%'
OR crs_cde LIKE 'THE-607%'
OR crs_cde LIKE 'THE-608%'
OR crs_cde LIKE 'THE-615%'
OR crs_cde LIKE 'THE-614%'
OR crs_cde LIKE 'THE-601%'
OR crs_cde LIKE 'THE-602%'
OR crs_cde LIKE 'THE-603%'
OR crs_cde LIKE 'THE-604%'
OR crs_cde LIKE 'THE-605%'
OR crs_cde LIKE 'THE-619%'
OR crs_cde LIKE 'THE-613%'
OR crs_cde LIKE 'THE-715%'
OR crs_cde LIKE 'THE-641%'
OR crs_cde LIKE 'THE-691%'
OR crs_cde LIKE 'THE-692%'
OR crs_cde LIKE 'THE-694%'
OR crs_cde LIKE 'THE-780%';
UPDATE CLASS SET priority=0
WHERE comp_id IS NULL;
""".split(';')[:-1]


def upload_transcript(filepath=None):
    """
    Upload a transcript excel file to database.

    Requires a database connection.

    The excel sheet provided must contain the following columns:
        stud_id,
        stud_first,
        stud_last,
        yr_cde,
        trm_cde,
        crs_cde,
        transaction_sts,
        crs_div,
        instrctr_id,
        last_pre_first_middle,
        instrctr_type,
        description,
        instrctr_fist,
        instrctr_last,
        pre

    Parameters:
    filepath (str): relative or absolute path to the transcript xlsx

    """
    # If a file was not provided, use the gui selector
    if not filepath:
        print('\nPlease select a transcript file...')
        filepath = askopenfilename(title='Select Transcript File',
                                   filetypes=(
                                       ('Excel Files', '*.xlsx'),
                                       ('all files', '*.*')))

    print(f'\nUsing file: {filepath}\n')

    start = time()

    progress(0, 6, "Pulling Data from Excel File                      ")

    # Get excel sheet
    sheet_df = pd.read_excel(filepath)

    con = db_engine.connect()

    progress(1, 6, "Processing Data                                   ")

    # Get students from excel sheet
    student_df = sheet_df[['stud_id', 'stud_first', 'stud_last']]
    student_df = student_df.drop_duplicates(subset='stud_id')
    student_df.columns = ['student_id', 'first_name', 'last_name']

    # Get instructors from excel sheet
    instructor_df = sheet_df[['instrctr_id', 'last_pre_first_middle',
                              'instrctr_type', 'description', 'instrctr_last',
                              'instrctr_first', 'pre']]

    instructor_df = instructor_df.drop_duplicates(subset='instrctr_id')

    # Rename columns to match database
    instructor_df.columns = ['instructor_id', 'last_pre_first_middle',
                             'instructor_type', 'description', 'last_name',
                             'first_name', 'pre']

    # Get courses from excel sheet
    class_df = sheet_df[['instrctr_id', 'yr_cde', 'trm_cde', 'crs_cde',
                         'crs_div']]

    # Add class_id column
    class_df.insert(0, 'class_id', '')

    def course_id(row):
        """Create course id out of row, needed for lambda."""
        return str(row['yr_cde']) + '-' + str(row['trm_cde']) + '-' \
            + row['crs_cde'].replace('  ', '-'). \
            replace(' ', '') + '-' + row['crs_div']

    # Set class ids
    class_df.loc[:, 'class_id'] = class_df.apply(
        lambda row: course_id(row), axis=1)
    class_df = class_df.drop_duplicates(subset='class_id')

    # Add priority column
    class_df.insert(6, 'priority', 0)

    # Add comp colum
    class_df.insert(7, 'comp_id', None)

    # Rename columns to match database
    class_df.columns = ['class_id', 'instructor_id', 'yr_cde', 'trm_cde',
                        'crs_cde', 'crs_div', 'priority', 'comp_id']

    # Get transcript from excel sheet
    transcript_df = sheet_df[['stud_id', 'yr_cde', 'trm_cde', 'crs_cde',
                              'crs_div', 'transaction_sts']]

    # Add class_id column
    transcript_df.insert(1, 'class_id', '')

    # Set class ids
    transcript_df.loc[:, 'class_id'] = transcript_df.apply(
        lambda row: course_id(row), axis=1)

    # Remove unneeded columns
    transcript_df = transcript_df.drop(
        ['yr_cde', 'trm_cde', 'crs_cde', 'crs_div'], axis=1
    )

    # Rename columns to match database
    transcript_df.columns = ['student_id', 'class_id', 'transaction_status']

    progress(2, 6, "Uploading Student Data                            ")

    # Append to STUDENT table via temp table
    student_df.to_sql('temp', con=db_engine, if_exists='replace', index=False)
    con.execute("INSERT IGNORE INTO STUDENT SELECT * FROM temp")

    progress(3, 6, "Uploading Instructor Data                         ")

    # Append to INSTRUCTOR table via temp table
    instructor_df.to_sql('temp', con=db_engine,
                         if_exists='replace', index=False)
    con.execute("INSERT IGNORE INTO INSTRUCTOR SELECT * FROM temp")

    progress(4, 6, "Uploading Course Data                             ")

    # Append to CLASS table via temp table
    class_df.to_sql('temp', con=db_engine, if_exists='replace', index=False)
    con.execute("INSERT IGNORE INTO CLASS SELECT * FROM temp")
    for snip in priority_sql:
        con.execute(snip)

    progress(5, 6, "Uploading Transcript Data                         ")

    # Append to TRANSCRIPT table via temp table
    transcript_df.to_sql('temp', con=db_engine,
                         if_exists='replace', index=False)
    con.execute("INSERT IGNORE INTO TRANSCRIPT SELECT * FROM temp")

    con.execute("DROP TABLE temp")

    con.close()

    progress(6, 6, "All Done                                          ")

    end = time()
    print(f'\n\nProcess took {end - start} seconds\n')


# Allow file to be run as standalone script
if __name__ == '__main__':
    upload_transcript()
