def bytes_to_int(byte):
    return int.from_bytes(byte,'big')

def int_to_bytes(int_):
    return int_.to_bytes((int_.bit_length() + 7) // 8, 'big')


def write_sector(data):
    data_lenght = int_to_bytes(len(data))
    return int_to_bytes(len(data_lenght)) + data_lenght + data

def write_sectors(list_data):
    all_info = b''
    for i in list_data:
        all_info += write_sector(i)
    return all_info

def read_sectors(data):
    out = []
    index = 0
    while index < len(data):
        length_of_header = data[index]
        dat_length = bytes_to_int(data[index+1:index+1+length_of_header])
        part_of_data = data[index+1+length_of_header:index+1+dat_length+length_of_header]
        out.append(part_of_data)
        index = index+length_of_header+dat_length+1
    return out


class sectorstype:
    def __init__(self,num_of_sectors):
        self.data=b''
        self.nos=num_of_sectors

    def add(self,info):
        self.data+=write_sector(write_sectors(info))

    def find(self,field_num,query):
        for en,sector in enumerate(read_sectors(self.data)):
            fields = read_sectors(sector)
            if fields[field_num] == query:
                return en
        return -1

    def rem(self,sector_num):
        sects = read_sectors(self.data)
        sects.pop(sector_num)
        self.data = write_sectors(sects)

    def save(self,filename):
        open(filename,'wb').write(self.data)

    def load(self,filename):
        self.data += open(filename,'rb').read()

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
        fields = read_sectors(read_sectors(self.data)[sector_num])
        if len(fields)-1 < field_num:
            return b''
        return fields[field_num]

    def fields(self,field_num):
        out = []
        for sector in read_sectors(self.data):
            out.append(read_sectors(sector)[field_num])
        return out