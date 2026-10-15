WITH history AS (
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
SELECT * FROM raises ORDER BY percentage_raise DESC, emp_no;
