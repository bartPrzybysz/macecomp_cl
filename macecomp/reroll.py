from time import time
from random import choices

import pandas as pd

# Relative imports behave differently based on wether this is run as
# a part of the package or as a standalone script
if __name__ == '__main__':
    from utils import progress, db_engine
else:
    from .utils import progress, db_engine

student_info_sql = """
SELECT CONCAT(first_name, ' ', last_name) AS 'name', 10Q.*
FROM 10Q
LEFT JOIN STUDENT ON 10Q.student_id=STUDENT.student_id
WHERE 10Q.student_id={student_id}
""".strip()

question_priority_sql = """
SELECT COMP.comp_id, CLASS.priority
FROM COMP
LEFT JOIN CLASS on COMP.comp_id=CLASS.comp_id
WHERE COMP.comp_id IN {question_ids}
GROUP BY COMP.comp_id
""".strip()

update_4q_sql = """
UPDATE 4Q SET Q1={}, Q2={}, Q3={}, Q4={}
WHERE student_id={student_id}
""".strip()


def reroll(student_id=None):
    """
    Randomly assign 4 new exam questions to a student

    Requires a db connection
    """

    print('')

    if not student_id:
        student_id = input('Please provide a student id: ')

    priority_weights = {1: 0.4, 2: 0.6}

    con = db_engine.connect()

    # Get name and 10Q questions
    result = con.execute(student_info_sql.format(student_id=student_id))
    student_info = result.fetchone()
    student_name = student_info[0]
    comp_ids = tuple(c for c in student_info[2:] if c is not None)

    # Double check
    if 'y' not in input(
            f'Randomly assign new questions to {student_name}? (y/n): '
            .lower()):
        return

    print('')

    start = time()

    progress(0, 3, 'Getting comp details                              ')

    # Get priorities of 10Q questions
    result = con.execute(question_priority_sql.format(
        question_ids=str(comp_ids)))
    comp_info = result.fetchall()
    _, priorities = zip(*comp_info)

    progress(1, 3, 'Picking new comp questions                        ')

    # Select 4 random questions
    weights = tuple(priority_weights[p] for p in priorities)
    random_selection = choices(population=comp_ids, weights=weights, k=4)

    progress(2, 3, 'Uploading results                                 ')

    # Update 4Q for student
    con.execute(update_4q_sql.format(*random_selection, student_id=student_id))

    con.close()

    progress(3, 3, "All Done                                          ")

    end = time()
    print(f'\n\nProcess took {end - start} seconds\n')


if __name__ == '__main__':
    reroll()
