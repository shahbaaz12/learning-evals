# HR question rules

- This is a fictional learning dataset, with annual salary in INR.
- Use the fixed reporting date **2026-10-01** instead of today's date.
- A dated row is active when `from_date <= reporting_date AND to_date > reporting_date`.
- `9999-01-01` means the record has no planned end date.
- A current employee has an active department assignment on the reporting date.
- Salary reports use an active salary row and an active department assignment.
- An employee can have historical department and salary records. Do not count those as current.
- Keep departments with no current employees when asked for all departments.
- Round averages and percentage changes to two decimal places.
- Two highest salary ranks means two distinct salaries; include everyone tied at either rank.
- Previous salary means the immediately preceding salary period, not the smallest historical salary.
- Return the columns and ordering requested in the question. Missing averages are SQL NULL.
