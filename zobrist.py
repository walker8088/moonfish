
import numpy as np

from random import randint

zobrist_table = np.random.randint(0, 0x8000000000000000, size=(14,256),dtype = np.int64)
#zobrist_table_check[14][256]
print(zobrist_table)

def rand32():
    return randint()

def rand64():
    return randint() << 32 + randint()
    
def init_zobrist_table(table):
    #for x in table.shape()[0]:
    pass   
    #return [rand64() for y in range(14) for x in range(256)]] 