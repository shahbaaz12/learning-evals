SELECT d.dept_name, COUNT(de.emp_no) AS employee_count,
       ROUND(AVG(s.salary), 2) AS average_salary
FROM departments d
LEFT JOIN dept_emp de ON de.dept_no = d.dept_no
 AND de.from_date <= '2026-10-01' AND de.to_date > '2026-10-01'
LEFT JOIN salaries s ON s.emp_no = de.emp_no
 AND s.from_date <= '2026-10-01' AND s.to_date > '2026-10-01'
GROUP BY d.dept_no, d.dept_name ORDER BY d.dept_name;
