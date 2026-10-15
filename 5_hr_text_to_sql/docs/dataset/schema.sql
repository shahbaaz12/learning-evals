-- SQLite adaptation of the MySQL Employees sample schema.
-- Source: https://github.com/datacharmer/test_db/blob/master/employees.sql
-- Original schema: Giuseppe Maxia, Patrick Crews, MySQL AB; CC BY-SA 3.0.
-- Changes: SQLite types, gender CHECK, ISO date strings, no MySQL views/DDL.
CREATE TABLE employees (
    emp_no INTEGER PRIMARY KEY, birth_date TEXT NOT NULL,
    first_name TEXT NOT NULL, last_name TEXT NOT NULL,
    gender TEXT NOT NULL CHECK (gender IN ('M', 'F')), hire_date TEXT NOT NULL
);
CREATE TABLE departments (dept_no TEXT PRIMARY KEY, dept_name TEXT NOT NULL UNIQUE);
CREATE TABLE dept_emp (
    emp_no INTEGER REFERENCES employees(emp_no),
    dept_no TEXT REFERENCES departments(dept_no),
    from_date TEXT NOT NULL, to_date TEXT NOT NULL,
    PRIMARY KEY (emp_no, dept_no)
);
CREATE TABLE dept_manager (
    emp_no INTEGER REFERENCES employees(emp_no),
    dept_no TEXT REFERENCES departments(dept_no),
    from_date TEXT NOT NULL, to_date TEXT NOT NULL,
    PRIMARY KEY (emp_no, dept_no)
);
CREATE TABLE titles (
    emp_no INTEGER REFERENCES employees(emp_no), title TEXT NOT NULL,
    from_date TEXT NOT NULL, to_date TEXT NOT NULL,
    PRIMARY KEY (emp_no, title, from_date)
);
CREATE TABLE salaries (
    emp_no INTEGER REFERENCES employees(emp_no), salary INTEGER NOT NULL,
    from_date TEXT NOT NULL, to_date TEXT NOT NULL,
    PRIMARY KEY (emp_no, from_date)
);
