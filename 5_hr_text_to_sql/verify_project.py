"""Offline checks for the fixture, evaluator, and budget. No API calls."""
import json
import sqlite3

from models.settings import DATA, DATABASE
from tools.budget import monthly_cost, shortlist
from tools.evaluation import execute_sql, load_goldens, same_answer


def verify():
    cases = load_goldens()
    assert len(cases) == 6
    assert [c['difficulty'] for c in cases] == ['simple'] * 2 + ['intermediate'] * 2 + ['difficult'] * 2
    for case in cases:
        assert same_answer(execute_sql(case['reference_sql']), case), case['id']
    # Equivalent SQL with different aliases still passes.
    alias_sql = 'SELECT dept_no AS id, dept_name AS name FROM departments ORDER BY dept_name'
    assert same_answer(execute_sql(alias_sql), cases[0])
    assert not same_answer(execute_sql('SELECT dept_no, dept_name FROM departments ORDER BY dept_name DESC'), cases[0])
    assert not same_answer(execute_sql('SELECT dept_name, dept_no FROM departments ORDER BY dept_name'), cases[0])
    assert not same_answer(execute_sql('SELECT dept_no, dept_name FROM departments WHERE dept_name != \'Research\' ORDER BY dept_name'), cases[0])
    unordered = dict(columns=['value'], rows=[[1], [1]], order_matters=False)
    assert not same_answer(dict(columns=['alias'], rows=[[1]], error=None), unordered)
    assert not same_answer(dict(columns=['alias'], rows=[[0]], error=None),
                           dict(columns=['value'], rows=[[None]], order_matters=True))
    assert execute_sql('SELECT unknown_column FROM employees')['error']
    assert execute_sql('DELETE FROM employees')['error']
    assert execute_sql('WITH x AS (SELECT 1) DELETE FROM employees')['error']
    assert execute_sql('SELECT 1; SELECT 2;')['error']
    connection = sqlite3.connect(DATABASE)
    assert connection.execute('SELECT COUNT(*) FROM employees').fetchone()[0] == 24
    assert not connection.execute('PRAGMA foreign_key_check').fetchall()
    connection.close()
    budget = json.loads((DATA / 'budget.json').read_text(encoding='utf-8'))
    assert round(monthly_cost(0.30, 1.20, budget), 2) == 3283.20
    assert monthly_cost(1.36, 4.18, budget) > budget['monthly_budget_inr']
    report = shortlist()
    assert len(report['shortlisted']) == 4
    assert all(row['monthly_inr'] <= 10000 for row in report['shortlisted'])
    print('Offline checks passed: six goldens, equivalent SQL, wrong tables, ordering, duplicates, NULL, SQL errors, read-only data, and budget.')


if __name__ == '__main__':
    verify()
