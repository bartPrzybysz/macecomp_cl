from time import time

import pandas as pd

# Relative imports behave differently based on wether this is run as
# a part of the package or as a standalone script
if __name__ == '__main__':
    from utils import progress, db_engine
else:
    from .utils import progress, db_engine


data_sql = """
SELECT TRANSCRIPT.student_id, TRANSCRIPT.transaction_status, CLASS.class_id,
       CLASS.priority, CLASS.comp_id, COMP.grading_instructor
FROM TRANSCRIPT
LEFT JOIN CLASS ON CLASS.class_id=TRANSCRIPT.class_id
LEFT JOIN COMP ON CLASS.comp_id = COMP.comp_id
WHERE CLASS.comp_id IS NOT NULL
AND TRANSCRIPT.student_id NOT IN (
    SELECT student_id FROM 4Q
)
ORDER BY TRANSCRIPT.student_id
""".strip()


def assign_questions():
    """
    Assign 10 study and 4 exam questions to each student who qulifies
    for comps and has no questions assigned yet

    Requires a db connection
    """

    print('')

    con = db_engine.connect()

    start = time()

    progress(0, 1, 'Pulling Data From Database                        ')

    # Get data from database
    data_df = pd.read_sql_query(data_sql, db_engine)

    # Filter out students who have taken less than 8 classes
    data_df = data_df.groupby('student_id').filter(lambda x: len(x) >= 8)

    student_count = len(data_df.groupby('student_id'))

    # Dataframes that reflect 10Q and 4Q tables in structure
    tenq_df = pd.DataFrame(
        columns=['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10'],
        index=data_df['student_id'].drop_duplicates()
    )
    fourq_df = pd.DataFrame(
        columns=['Q1', 'Q2', 'Q3', 'Q4'],
        index=data_df['student_id'].drop_duplicates()
    )

    task_counter = 1

    # Iterate over individual stuennt transcripts
    for student_id, transcript in data_df.groupby('student_id'):
        progress(
            task_counter, student_count + 3,
            f'Assigning Questions to Student {student_id}              '
        )
        task_counter += 1

        ################################################################
        #                   Assign Study Questions                     #
        ################################################################

        # Set of transcript indexes of selected classes
        selection = set()
        # Set of instructors that have not yet been used
        distinct_prof = set(transcript['grading_instructor'])

        # ---- Step 1: Assign no more than 6 priority 2 questions ---- #

        if len(transcript.query('priority == 2')) <= 6:
            # add all priority 2 questions to selection
            selection.update(set(transcript.query('priority == 2').index))

            # Remove newly selected instructos from distinct_prof
            distinct_prof -= set(transcript.loc[selection,
                                                'grading_instructor'])

        else:  # If there are more than 6 priority 2 questions
            while len(selection) < 6:

                # Set of unused priority 2 instructors
                p2_distinct_prof = set(transcript.query(
                    'priority == 2 and ' +
                    'grading_instructor in @distinct_prof and ' +
                    'index not in @selection'
                ).grading_instructor)

                # List of transcript indexes to choose from
                candidates = set()

                # If there are still unused priority 2 instructors,
                if p2_distinct_prof:
                    # choose from their transcript entries
                    candidates = set(transcript.query(
                        'priority == 2 and ' +
                        'grading_instructor in @p2_distinct_prof and ' +
                        'index not in @selection'
                    ).index)

                else:  # If there are no more unused priority 2 instructors
                    # Use any unused priority 2 transcript entry
                    candidates = set(transcript.query(
                        'priority == 2 and ' +
                        'index not in @selection'
                    ).index)

                # Choose one at random from candidates
                selected_row = transcript.loc[candidates].sample()

                # Add selected index to selection
                selection.update(set(selected_row.index))
                # Remove selected instructor from distinct_prof
                distinct_prof -= set(selected_row.grading_instructor)

        # ------ Step 2: Try to fill selection with priority 1 ------- #

        # If the number of priority 1 questions is less than or equal to
        # number of free slots in selection
        if len(transcript.query('priority == 1')) + len(selection) <= 10:
            # Add all priority 1 questions to selection
            selection.update(set(transcript.query('priority == 1').index))

            # Remove newly selected instructos from distinct_prof
            distinct_prof -= set(transcript.loc[selection,
                                                'grading_instructor'])

        else:  # If there are more questions than slots

            # While there are open slots in selection and there are
            # unused priority 1 questions
            while len(selection) < 10 and \
                    len(transcript.query(
                        'priority == 1 and index not in @selection'
                    )) > 0:

                # Set of unused priority 1 instructors
                p1_distinct_prof = set(transcript.query(
                    'priority == 1 and ' +
                    'grading_instructor in @distinct_prof and ' +
                    'index not in @selection'
                ).grading_instructor)

                # List of transcript indexes to choose from
                candidates = set()

                # If tehre are still unused priority 1 instructors,
                if p1_distinct_prof:
                    # choose from their transcript entries
                    candidates = set(transcript.query(
                        'priority == 1 and ' +
                        'grading_instructor in @p1_distinct_prof and ' +
                        'index not in @selection'
                    ).index)

                else:  # If there are no more unused priority 1 instrucotrs
                    # Use any unused priority 1 transcript entry
                    candidates = set(transcript.query(
                        'priority == 1 and ' +
                        'index not in @selection'
                    ).index)

                # Choose one at random from candidates
                selected_row = transcript.loc[candidates].sample()
                # Add selected index to selection
                selection.update(set(selected_row.index))
                # Remove selected instructor from distinct_prof
                distinct_prof -= set(selected_row.grading_instructor)

        # ----- Step 3: Make sure selection is completely filled ----- #

        if len(selection) < 10:

            # Set of unused entries
            unused = set(transcript.query(
                'index not in @selection'
            ).index)

            while unused and len(selection) < 10:
                rand_select = list(transcript.loc[unused].sample().index)[0]
                selection.add(rand_select)
                unused.remove(rand_select)

        # ----------------- Add results to tenq_df ------------------- #

        tenq_df.loc[student_id, :len(selection)] = list(
            transcript.loc[selection].comp_id)

        ################################################################
        #                   Assign Exam Questions                      #
        ################################################################

        # Set of transcript indexes of selected exam questions
        exam = set()

        selection_df = transcript.loc[selection]

        # Distinct_prof now contains selected instructors that are not
        # yet used in Exam questions
        distinct_prof = set(selection_df.grading_instructor)

        # Step 1: If selection has any priority 2 questions, make sure #
        # ----------------- at least one is used --------------------- #

        # if there is a priority 2 in selection
        if 2 in set(selection_df.priority):
            rand_select = selection_df.query('priority == 2').sample()
        else:  # pick random selection
            rand_select = selection_df.sample()

        exam.update(set(rand_select.index))
        distinct_prof -= set(rand_select.grading_instructor)

        # - Step 2: Pick a random selection, unused prof if possible - #

        if distinct_prof:
            candidates = set(selection_df.query(
                'grading_instructor in @distinct_prof and ' +
                'index not in @exam'
            ).index)
        else:
            candidates = set(selection_df.query(
                'index not in @exam'
            ).index)

        rand_select = selection_df.loc[candidates].sample()

        exam.update(set(rand_select.index))
        distinct_prof -= set(rand_select.grading_instructor)

        # --- Step 3: Try to fill remaining spots with priority 1, --- #
        # ---------------- unused prof if possible ------------------- #

        while len(exam) < 4:
            if distinct_prof:
                candidates = set(selection_df.query(
                    'priority == 1 and ' +
                    'grading_instructor in @distinct_prof and ' +
                    'index not in @exam'
                ).index)
            else:
                candidates = set(selection_df.query(
                    'priority == 1 and ' +
                    'index not in @exam'
                ).index)

            if len(candidates) < 2:
                if distinct_prof:
                    candidates = set(selection_df.query(
                        'grading_instructor in @distinct_prof and ' +
                        'index not in @exam'
                    ).index)
                else:
                    candidates = set(selection_df.query(
                        'index not in @exam'
                    ).index)

            rand_select = selection_df.loc[candidates].sample()

            exam.update(set(rand_select.index))
            distinct_prof -= set(rand_select.grading_instructor)

        # ---------------- Add results to fourq_df ------------------- #

        fourq_df.loc[student_id, :] = list(transcript.loc[exam].comp_id)

    progress(
        task_counter, student_count + 2,
        'Uploading Questions to Database                          '
    )

    # Append to 10Q table via temp table
    tenq_df.to_sql('temp', con=db_engine, if_exists='replace', index=True)
    con.execute("INSERT IGNORE INTO 10Q SELECT * FROM temp")

    # Append to 4Q table via temp table
    fourq_df.to_sql('temp', con=db_engine, if_exists='replace', index=True)
    con.execute("INSERT IGNORE INTO 4Q SELECT * FROM temp")

    con.execute("DROP TABLE temp")

    con.close()

    progress(1, 1, 'All Done                                          ')

    end = time()
    print(f'\n\nProcess took {end - start} seconds\n')


# Allow file to be run as standalone script
if __name__ == '__main__':
    assign_questions()
