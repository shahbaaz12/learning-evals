WITH ranked AS (
 SELECT d.dept_name, e.emp_no, e.first_name, e.last_name, s.salary,
 DENSE_RANK() OVER (PARTITION BY d.dept_no ORDER BY s.salary DESC) AS salary_rank
 FROM employees e JOIN dept_emp de ON de.emp_no = e.emp_no
 JOIN departments d ON d.dept_no = de.dept_no
 JOIN salaries s ON s.emp_no = e.emp_no
 WHERE de.from_date <= '2026-10-01' AND de.to_date > '2026-10-01'
 AND s.from_date <= '2026-10-01' AND s.to_date > '2026-10-01'
)
SELECT dept_name, emp_no, first_name, last_name, salary, salary_rank
FROM ranked WHERE salary_rank <= 2 ORDER BY dept_name, salary_rank, emp_no;
