"""Build a small, deterministic fictional HR database. No model calls."""
import json
import sqlite3

from models.settings import DATA, DATABASE


def prepare_database():
    departments = [('d005', 'Development'), ('d007', 'Sales'),
                   ('d003', 'Human Resources'), ('d002', 'Finance'), ('d008', 'Research')]
    names = [('Asha', 'Rao'), ('Ben', 'Shah'), ('Cara', 'Das'), ('Dev', 'Sen'),
             ('Esha', 'Roy'), ('Farhan', 'Ali'), ('Gita', 'Nair'), ('Hari', 'Jain'),
             ('Isha', 'Bose'), ('Jay', 'Patel'), ('Kiran', 'Rana'), ('Leena', 'Paul'),
             ('Mohan', 'Singh'), ('Nina', 'Mehta'), ('Omar', 'Khan'), ('Priya', 'Iyer'),
             ('Qasim', 'Malik'), ('Rita', 'Kapoor'), ('Samar', 'Gupta'), ('Tara', 'Joshi'),
             ('Uma', 'Seth'), ('Vikram', 'Gill'), ('Wafa', 'Mir'), ('Yash', 'Bhat')]
    dept_ids = ['d005', 'd007', 'd003', 'd002'] + ['d005'] * 6 + ['d007'] * 4
    dept_ids += ['d003'] * 2 + ['d002'] * 4 + ['d005', 'd007', 'd003', 'd005']
    current = [120000, 110000, 100000, 130000, 110000, 110000, 90000, 80000,
               70000, 65000, 100000, 100000, 85000, 75000, 80000, 70000,
               115000, 90000, 80000, 70000, 150000, 180000, 95000, 140000]
    previous = [110000, 100000, 95000, 120000, 100000, 95000, 80000, 80000,
                65000, 60000, 90000, 95000, 70000, 75000, 70000, 65000,
                100000, 90000, 70000, None, 140000, 170000, 90000, None]
    tables = {name: [] for name in ['employees', 'departments', 'dept_emp',
                                   'dept_manager', 'titles', 'salaries']}
    tables['departments'] = departments
    for i, ((first, last), dept, salary, prior) in enumerate(zip(names, dept_ids, current, previous)):
        emp = 1001 + i
        hired = '2024-04-15' if emp in [1007, 1011, 1015, 1018, 1020, 1023] else '2020-01-01'
        if emp == 1024:
            hired = '2026-11-01'
        end = {1021: '2025-12-31', 1022: '2026-05-01', 1023: '2026-09-01'}.get(emp, '9999-01-01')
        tables['employees'].append((emp, f'1985-{i % 12 + 1:02d}-10', first, last,
                                    'F' if i % 2 == 0 else 'M', hired))
        start = hired
        if emp == 1010:
            tables['dept_emp'].append((emp, 'd007', hired, '2025-01-01'))
            start = '2025-01-01'
        tables['dept_emp'].append((emp, dept, start, end))
        title = 'Engineer' if dept == 'd005' else 'Staff'
        tables['titles'].append((emp, title, hired, end))
        if i < 4:
            tables['dept_manager'].append((emp, dept, hired, end))
        if prior is not None:
            boundary = '2025-01-01' if emp == 1021 else '2026-01-01'
            tables['salaries'].append((emp, prior, hired, boundary))
            tables['salaries'].append((emp, salary, boundary, end))
        else:
            tables['salaries'].append((emp, salary, hired, end))

    # Rebuild these six fixture tables explicitly; other files are untouched.
    connection = sqlite3.connect(DATABASE)
    for table in reversed(list(tables)):
        connection.execute(f'DROP TABLE IF EXISTS {table}')
    connection.executescript((DATA / 'schema.sql').read_text(encoding='utf-8'))
    connection.execute('PRAGMA foreign_keys = ON')
    for table, rows in tables.items():
        placeholders = ','.join('?' for _ in rows[0])
        connection.executemany(f'INSERT INTO {table} VALUES ({placeholders})', rows)
    connection.commit()
    assert not connection.execute('PRAGMA foreign_key_check').fetchall()
    connection.close()
    (DATA / 'seed.json').write_text(json.dumps(tables, indent=2) + '\n', encoding='utf-8')
    print({table: len(rows) for table, rows in tables.items()})


if __name__ == '__main__':
    prepare_database()
