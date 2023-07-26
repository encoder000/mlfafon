import random
import os
import rsa
import struct

WORDS = ['rain', 'a', 'did', 'the', 'speech', 'valleys', 'was', 'in', 'plaister', 'therein', 'israel', 'gannim', 'seek', 'now', 'depart', 'small', 'trieth', 'jabbok', 'meat', 'of', 'jordan', 'jesimiel', 'scribe', 'neither', 'praise', 'door', 'priest', 'will', 'them', 'be', 'no', 'jesus', 'to', 'jerome', 'all', 'land', 'and', 'zibeon', 'come', 'man', 'god', 'unto', 'until', 'had', 'give', 'by', 'statutes', 'thee', 'when', 'sword', 'king', 'ur', 'my', 'went', 'him', 'due', 'saith', 'lies', 'shall', 'his', 'precious', 'so', 'themselves', 'hold', 'brought', 'are', 'would', 'dan', 'dogmatize', 'son', 'as', 'if', 'zedekiah', 'heart', 'i', 'david', 'doings', 'written', 'asa', 'up', 'me', 'even', 'among', 'forth', 'hath', 'simon', 'meet', 'cried', 'leah', 'that', 'sorrow', 'according', 'walls', 'courage', 'at', 's', 'profitable', 'asked', 'stranger', 'into', 'blot', 'pass', 'hast', 'sepulchre', 'solomon', 'thou', 'said', 'judged', 'wife', 'affliction', 'money', 'might', 'forest', 'honourable', 'abraham', 'yet', 'with', 'he', 'people', 'have', 'though', 'faith', 'didst', 'lord', 'lay', 'shepherds', 'plead', 'father', 'jacob', 'hand', 'which', 'quicken', 'net', 'christ', 'thirteenth', 'house', 'benjamin', 'from', 'sons', 'fled', 'esau', 'years', 'remission', 'heareth', 'mother', 'despiteful', 'flourish', 'world', 'but', 'bring', 'on', 'clothed', 'merari', 'flowers', 'year', 'lawful', 'for', 'memphis', 'strengthened', 'watch', 'ready', 'also', 'then', 'saying', 'dash', 'chapter', 'polluted', 'offered', 'spoken', 'jephthah', 'every', 'your', 'through', 'bani', 'thy', 'slay', 'fellowship', 'hands', 'beareth', 'upon', 'is', 'talking', 'kind', 'four', 'ishmael', 'second', 'diligence', 'silver', 'can', 'we', 'creepeth', 'ye', 'out', 'works', 'joseph', 'an', 'hear', 'wood', 'duty', 'delivered', 'our', 'dieth', 'satisfied', 'evil', 'bread', 'am', 'despise', 'high', 'suburbs', 'exercendi', 'great', 'made', 'smitten', 'healing', 'tyre', 'their', 'other', 'gave', 'kissed', 'family', 'this', 'goat', 'unclean', 'day', 'or', 'rule', 'windows', 'any', 'grave', 'what', 'spirit', 'youngest', 'disciples', 'walkest', 'blains', 'nay', 'therefore', 'having', 'arise', 'who', 'kenaz', 'levites', 'daughter', 'fulfil', 'let', 'you', 'fat', 'three', 'blessed', 'whereof', 'kingdom', 'abhor', 'part', 'seen', 'abhorred', 'night']

def genseed():
    words = [WORDS[os.urandom(1)[0]] for i in range(10)]
    return ' '.join(words)

def readseed(seed):
    words = seed.split()
    words.reverse()
    outnum = 0
    for e,i in enumerate(words):
        index = WORDS.index(i)
        #print(e)
        outnum += 256**(e)*index
    return outnum

def setseed(seed):
    random.seed(readseed(seed))
    
def seed_read_random_bits(nbits: int) -> bytes:
    """Reads 'nbits' random bits.

    If nbits isn't a whole number of bytes, an extra byte will be appended with
    only the lower bits set.
    """

    nbytes, rbits = divmod(nbits, 8)

    # Get the random bytes
    randomdata = random.randbytes(nbytes)

    # Add the remaining random bits
    if rbits > 0:
        randomvalue = random.randint(0,255)
        randomvalue >>= 8 - rbits
        randomdata = struct.pack("B", randomvalue) + randomdata

    return randomdata

def seed_read_random_bits_normal(nbits: int) -> bytes:
    """Reads 'nbits' random bits.

    If nbits isn't a whole number of bytes, an extra byte will be appended with
    only the lower bits set.
    """

    nbytes, rbits = divmod(nbits, 8)

    # Get the random bytes
    randomdata = os.urandom(nbytes)

    # Add the remaining random bits
    if rbits > 0:
        randomvalue = random.randint(0,255)
        randomvalue >>= 8 - rbits
        randomdata = struct.pack("B", randomvalue) + randomdata

    return randomdata

rsa.randnum.read_random_bits = seed_read_random_bits

