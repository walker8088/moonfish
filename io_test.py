
from __future__ import print_function
import sys,time

# Python 2 compatability
if sys.version_info[0] == 2:
    input = raw_input

# Disable buffering
class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream
    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
    def __getattr__(self, attr):
        return getattr(self.stream, attr)
sys.stdout = Unbuffered(sys.stdout)


print("Ready")
    
while True:
    smove = input()
    print("Got", smove)
    if smove == 'ucci':
        print('ucciok')
    if smove == 'quit':
        break
