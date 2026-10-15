WITH current_development AS (
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
ORDER BY salary DESC, emp_no;
