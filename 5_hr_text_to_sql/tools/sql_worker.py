"""Execute one query in a read-only database. Errors exit this small process."""
import json
import re
import sqlite3
import sys
from pathlib import Path
from time import monotonic


if __name__ == '__main__':
    sql = sys.stdin.read().strip()
    assert re.match(r'^(SELECT|WITH)\b', sql, re.IGNORECASE), 'Return one SELECT query.'
    database = Path(sys.argv[1]).resolve()
    connection = sqlite3.connect(f'{database.as_uri()}?mode=ro', uri=True)
    connection.execute('PRAGMA query_only = ON')
    deadline = monotonic() + 5
    connection.set_progress_handler(lambda: int(monotonic() > deadline), 1000)
    cursor = connection.execute(sql)
    rows = cursor.fetchmany(1001)
    assert len(rows) <= 1000, 'Learning queries must return at most 1000 rows.'
    print(json.dumps(dict(columns=[c[0] for c in cursor.description], rows=rows)))
    connection.close()
