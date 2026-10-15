from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parent
DATA = PROJECT / 'docs' / 'dataset'
DATABASE = DATA / 'employees.sqlite'
AS_OF = '2026-10-01'
