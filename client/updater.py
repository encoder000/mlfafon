import requests
import shutil
import os
import sys

ver = '52'
n = requests.get('https://raw.githubusercontent.com/encoder000/mlfafon/main/newest.txt?').text[:-1]

if int(ver,16) < int(n,16):
    print('[+] Software updating.')
    full_ver = '.'.join([i for i in n])
    arch_name = f'mlfafon{full_ver}.zip'
    saved_arch_name = 'mlfafon-update.zip'
    extract_dir = os.path.dirname(os.getcwd())
    arch = requests.get(f'https://github.com/encoder000/mlfafon/releases/download/{full_ver}/{arch_name}').content
    open(saved_arch_name,'wb').write(arch)
    shutil.unpack_archive(saved_arch_name,extract_dir)
    print('[+] Updated. Plz restart mlfafon')
    sys.exit(0)
