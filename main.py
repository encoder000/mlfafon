from main_full.connection import get_server_ip, connect_to_server
from main_full.commands import handle_command
from main_full.commands import update
from main_full.helpers import create_program_data_folder, get_command

def main():
    create_program_data_folder()
    ip = get_server_ip()
    try:
        cli = connect_to_server(ip)
        while True:
            try:
                update(cli)
                cmd, dat = get_command('[+] Command: ')
                handle_command(cmd, dat, cli)
            except Exception as e:
                print(f'[-] Error: {e}')
    except KeyboardInterrupt:
        print('[-] Exiting program')

if __name__ == '__main__':
    main()
