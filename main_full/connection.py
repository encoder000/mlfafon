import client
import os
from main_full.helpers import create_program_data_folder, get_command
from main_full.account import create_account

def get_server_ip():
    default_ip = '185.117.155.43'
    ip = input(f'[+] IP of server (default {default_ip}): ')
    if not ip:
        ip = default_ip
    return ip

def connect_to_server(ip):
    print('[!] To connect use "connect" command and to make an account, use "acc" command')
    connected = False
    while not connected:
        cmd, dat = get_command('[+] Command: ')
        if cmd == 'acc':
            create_account()
        elif cmd == 'connect':
            account_name = input('[+] Account name: ')
            password = input('[+] Password: ').encode()
            username = input('[+] Username, which you want to have: ').encode()
            try:
                cli = client.mlaffon(account_name, password, username, ip)
                cli.connect()
                while cli.auth() == -1:
                    print('[-] Invalid username')
                    account_name = input('[+] Account name: ')
                    password = input('[+] Password: ').encode()
                    username = input('[+] Username, which you want to have: ').encode()
                    cli = client.mlaffon(account_name, password, username, ip)
                    cli.connect()
                connected = True
            except Exception as e:
                print(f'[-] Error connecting to server: {e}')
    return cli
