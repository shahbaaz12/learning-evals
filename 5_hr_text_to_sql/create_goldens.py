"""Save six questions, reference SQL, and executed result tables."""
import hashlib
import json
import sqlite3

from models.settings import AS_OF, DATA, DATABASE, PROJECT


CASES = [
    ('q001', 'simple',
     'List all department IDs and department names, ordered by department name.',
     'SELECT dept_no, dept_name FROM departments ORDER BY dept_name;'),
    ('q002', 'simple',
     'List the employee ID, first name, last name, and hire date of everyone hired in 2024, including former employees. Order by employee ID.',
     "SELECT emp_no, first_name, last_name, hire_date FROM employees WHERE hire_date >= '2024-01-01' AND hire_date < '2025-01-01' ORDER BY emp_no;"),
    ('q003', 'intermediate',
     'As of 2026-10-01, show every department name, its current employee count, and average current annual salary rounded to two decimals. Include empty departments with count 0 and average NULL. Order by department name.',
     """SELECT d.dept_name, COUNT(de.emp_no) AS employee_count,
       ROUND(AVG(s.salary), 2) AS average_salary
FROM departments d
LEFT JOIN dept_emp de ON de.dept_no = d.dept_no
 AND de.from_date <= '2026-10-01' AND de.to_date > '2026-10-01'
LEFT JOIN salaries s ON s.emp_no = de.emp_no
 AND s.from_date <= '2026-10-01' AND s.to_date > '2026-10-01'
GROUP BY d.dept_no, d.dept_name ORDER BY d.dept_name;"""),
    ('q004', 'intermediate',
     'As of 2026-10-01, which current Development employees earn more than the average current Development salary? Return employee ID, first name, last name, and annual salary. Order by salary descending, then employee ID ascending.',
     """WITH current_development AS (
 SELECT e.emp_no, e.first_name, e.last_name, s.salary
 FROM employees e JOIN dept_emp de ON de.emp_no = e.emp_no
 JOIN departments d ON d.dept_no = de.dept_no
 JOIN salaries s ON s.emp_no = e.emp_no
 WHERE d.dept_name = 'Development'
 AND de.from_date <= '2026-10-01' AND de.to_date > '2026-10-01'
 AND s.from_date <= '2026-10-01' AND s.to_date > '2026-10-01'
)
SELECT emp_no, first_name, last_name, salary FROM current_development
WHERE salary > (SELECT AVG(salary) FROM current_development)
ORDER BY salary DESC, emp_no;"""),
    ('q005', 'difficult',
     'As of 2026-10-01, list current employees at the two highest distinct salary ranks in each department, including ties. Return department name, employee ID, first name, last name, salary, and salary rank. Order by department name, rank, then employee ID.',
     """WITH ranked AS (
 SELECT d.dept_name, e.emp_no, e.first_name, e.last_name, s.salary,
 DENSE_RANK() OVER (PARTITION BY d.dept_no ORDER BY s.salary DESC) AS salary_rank
 FROM employees e JOIN dept_emp de ON de.emp_no = e.emp_no
 JOIN departments d ON d.dept_no = de.dept_no
 JOIN salaries s ON s.emp_no = e.emp_no
 WHERE de.from_date <= '2026-10-01' AND de.to_date > '2026-10-01'
 AND s.from_date <= '2026-10-01' AND s.to_date > '2026-10-01'
)
SELECT dept_name, emp_no, first_name, last_name, salary, salary_rank
FROM ranked WHERE salary_rank <= 2 ORDER BY dept_name, salary_rank, emp_no;"""),
    ('q006', 'difficult',
     'As of 2026-10-01, which current employees received at least a 10 percent raise from their immediately previous salary to their current salary? Exclude employees with no previous salary. Return employee ID, first name, last name, current department name, previous salary, current salary, and percentage raise rounded to two decimals. Order by percentage raise descending, then employee ID ascending.',
     """WITH history AS (
 SELECT emp_no, salary, from_date, to_date,
 LAG(salary) OVER (PARTITION BY emp_no ORDER BY from_date) AS previous_salary
 FROM salaries WHERE from_date <= '2026-10-01'
), raises AS (
 SELECT e.emp_no, e.first_name, e.last_name, d.dept_name,
 h.previous_salary, h.salary AS current_salary,
 ROUND(100.0 * (h.salary - h.previous_salary) / h.previous_salary, 2) AS percentage_raise
 FROM history h JOIN employees e ON e.emp_no = h.emp_no
 JOIN dept_emp de ON de.emp_no = e.emp_no
 JOIN departments d ON d.dept_no = de.dept_no
 WHERE h.to_date > '2026-10-01'
 AND de.from_date <= '2026-10-01' AND de.to_date > '2026-10-01'
 AND h.previous_salary IS NOT NULL
 AND 100 * (h.salary - h.previous_salary) >= 10 * h.previous_salary
)
SELECT * FROM raises ORDER BY percentage_raise DESC, emp_no;"""),
]


def prepare_goldens():
    folder = PROJECT / 'docs' / 'goldends'
    connection = sqlite3.connect(f'{DATABASE.as_uri()}?mode=ro', uri=True)
    cases = []
    for case_id, difficulty, question, sql in CASES:
        cursor = connection.execute(sql)
        columns = [column[0] for column in cursor.description]
        rows = [list(row) for row in cursor.fetchall()]
        cases.append(dict(id=case_id, difficulty=difficulty, question=question,
                          reference_sql=sql, columns=columns, rows=rows, order_matters=True))
        (folder / f'{case_id}.sql').write_text(sql + '\n', encoding='utf-8')
        (folder / f'{case_id}_result.json').write_text(
            json.dumps(dict(columns=columns, rows=rows), indent=2) + '\n', encoding='utf-8')
    connection.close()
    # These checks were calculated separately from the reference SQL.
    assert cases[0]['rows'] == [['d005', 'Development'], ['d002', 'Finance'],
                              ['d003', 'Human Resources'], ['d008', 'Research'], ['d007', 'Sales']]
    assert [r[0] for r in cases[1]['rows']] == [1007, 1011, 1015, 1018, 1020, 1023]
    assert cases[2]['rows'] == [
        ['Development', 7, 92142.86], ['Finance', 5, 97000.0],
        ['Human Resources', 3, 83333.33], ['Research', 0, None], ['Sales', 5, 94000.0]]
    assert [r[0] for r in cases[3]['rows']] == [1001, 1005, 1006]
    assert [r[1] for r in cases[4]['rows']] == [1001, 1005, 1006, 1004, 1017, 1003, 1015, 1002, 1011, 1012]
    assert [r[0] for r in cases[5]['rows']] == [1013, 1006, 1017, 1015, 1019, 1007, 1011, 1002, 1005]
    document = dict(as_of=AS_OF, human_review='pending',
                    database_sha256=hashlib.sha256(DATABASE.read_bytes()).hexdigest(),
                    seed_sha256=hashlib.sha256((DATA / 'seed.json').read_bytes()).hexdigest(),
                    schema_sha256=hashlib.sha256((DATA / 'schema.sql').read_bytes()).hexdigest(),
                    cases=cases)
    (folder / 'goldens.json').write_text(json.dumps(document, indent=2) + '\n', encoding='utf-8')
    (DATA / 'questions.json').write_text(json.dumps([
        {k: c[k] for k in ['id', 'difficulty', 'question']} for c in cases], indent=2) + '\n', encoding='utf-8')
    print('Saved six reference queries and result tables; independent expected-value checks passed.')


if __name__ == '__main__':
    prepare_goldens()
