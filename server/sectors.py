import os
import zlib
import simp_aes
import aes

def bytes_to_int(byte):
    return int.from_bytes(byte,'big')

def int_to_bytes(int_):
    if int_ == 0:
        return b'\x00'
    return int_.to_bytes((int_.bit_length() + 7) // 8, 'big')


def write_sector(data):
    data_lenght = int_to_bytes(len(data))
    return bytes([len(data_lenght)]) + data_lenght + data

def write_sectors(list_data):
    all_info = b''
    for i in list_data:
        all_info += write_sector(i)
    return all_info

def reader(data):
    index = 0
    iterer = 0
    while index < len(data):
        length_of_header = data[index]
        index+=1
        dat_length = bytes_to_int(data[index:index+length_of_header])
        index+=length_of_header
        part_of_data = data[index:index+dat_length]
        index += dat_length
        yield iterer,part_of_data
        iterer+=1

def read_sectors(data):
    return [i[1] for i in reader(data)]


class sectorstype:
    def __init__(self,filename=None,key=0):
        self.data=b''
        self.filename = filename
        if key:
            self.key = aes.aes(simp_aes.get_aes_session_password(key),256)
        else:
            self.key = 0

    def add(self,info):
        self.data+=write_sector(write_sectors(info))

    def find(self,field_num,query):
        for en,sector in reader(self.data):
            if query in sector:
                fields = read_sectors(sector)
                if len(fields) >= field_num+1:
                    if fields[field_num] == query:
                        return en
        return -1

    def rem(self,sector_num):
        sects = read_sectors(self.data)
        sects.pop(sector_num)
        self.data = write_sectors(sects)

    def save(self):
        if self.filename:
            if self.key:
                open(self.filename,'wb').write(simp_aes.aes_full_encrypt(self.key,zlib.compress(self.data)))
            else:
                open(self.filename,'wb').write(self.data)

    def load(self):
        if not os.path.exists(self.filename):
            self.save()
        if self.key:
            self.data = zlib.decompress(simp_aes.aes_full_decrypt(self.key,open(self.filename,'rb').read()))
        else:
            self.data = open(self.filename,'rb').read()

    def edit(self,sector_num,field_num,data):
        tmpdat = read_sectors(self.data)
        to_put = read_sectors(tmpdat[sector_num])
        if len(to_put)-1>=field_num:
            to_put[field_num] = data
        else:
            to_put.append(data)
        tmpdat[sector_num] = write_sectors(to_put)
        self.data = write_sectors(tmpdat)

    def getdat(self,sector_num,field_num):
        for e,i in reader(self.data):
            if e == sector_num:
                for et,j in reader(i):
                    if et == field_num:
                        return j
        return b''

    def fields(self,field_num):
        out = []
        for e,sector in reader(self.data):
            out.append(read_sectors(sector)[field_num])
        return out

    def add_to_field(self,sector_num,field_num,data):
        new_data = self.getdat(sector_num,field_num)+data
        self.edit(sector_num,field_num,new_data)

    def intel_field_get(self,sector_num,field_num):
        obj = sectorstype()
        obj.data = self.getdat(sector_num,field_num)
        return obj

    def intel_field_set(self,sector_num,field_num,intel_field):
        self.edit(sector_num,field_num,intel_field.data)
        
