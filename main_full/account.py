import os
import sessions

PROGRAM_DATA_FOLDER = 'programdata'

def create_account():
    name = input('[+] Name: ')
    key = input('[+] Key: ')
    session_file = os.path.join(PROGRAM_DATA_FOLDER, f'{name}.sess')
    if os.path.exists(session_file):
        overwrite = input('This session file exists. Are you sure to rewrite it Y/(N): ').lower()
        if overwrite != 'y':
            return
    with open(session_file, 'wb') as f:
        f.write(sessions.gen_session(key.encode()))