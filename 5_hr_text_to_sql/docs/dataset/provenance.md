# Dataset source and limits

The starting reference is the [MySQL Employees installation guide](https://dev.mysql.com/doc/employee/en/employees-installation.html)
and its linked [test_db repository](https://github.com/datacharmer/test_db).
The [original schema](https://github.com/datacharmer/test_db/blob/master/employees.sql)
has employees, departments, department assignments, managers, titles, and salary history.

We adapted that structure for SQLite so this lesson needs no MySQL server.
Dates are ISO text; MySQL types and DDL were simplified. The adapted schema is
attributed to Giuseppe Maxia, Patrick Crews, and MySQL AB and shared under
[CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/), consistent with the
[Employees sample license](https://dev.mysql.com/doc/employee/en/employees-license.html).

All 24 employee records and salaries are newly generated fictional examples.
This is not a download or subset of the original employee records. The fixture has
20 current employees, three former employees, one future hire, one empty department,
a department transfer, salary ties, unchanged salaries, and a missing previous salary.
These cases make incorrect joins and date filters visible in the evaluation.

The six golden queries were AI-prepared and checked by execution plus independent
expected values. Human review is pending. Six examples are a learning pilot,
not enough evidence for production model selection. The current questions do not
evaluate manager/title queries; add those before expanding the use case.
