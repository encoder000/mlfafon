import os

PROGRAM_DATA_FOLDER = 'programdata'

def create_program_data_folder():
    if not os.path.exists(PROGRAM_DATA_FOLDER):
        os.mkdir(PROGRAM_DATA_FOLDER)

def get_command(inp):
    info = input(inp).split()
    cmd = info[0]
    dat = info[1:] if len(info) > 1 else []
    return cmd, dat
