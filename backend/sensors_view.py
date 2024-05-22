#!.venv/bin/python3
from models.db_engine.db import TempDB, FileDB

tmpdb = TempDB()
path = tmpdb.get_tmp_db_path()
curr_db_line = 0


while True:
    with FileDB(path, 'r') as db:
        lines = db.readlines()

    if curr_db_line != len(lines):
        print(lines[-1], end="")
    
    curr_db_line = len(lines)

    