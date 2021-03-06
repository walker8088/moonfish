#!/usr/bin/env pypy -u
# -*- coding: utf-8 -*-
from __future__ import print_function
import importlib
import re
import sys
import time

from moonfish import *
import tools

# Python 2 compatability
if sys.version_info[0] == 2:
    input = raw_input

'''
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
'''

def main():
    pos = tools.parseFEN('2ba3r1/5k3/b8/1n3N2C/4p4/3R2R2/9/5p1r1/4p4/5K3 w moves d4d8 d9e8 f6d7 b6d7 g4f4 d7f6 f4f6')#tools.FEN_INITIAL)
    searcher = Searcher()
    forced = False
    color = RED
    our_time, opp_time = 1000, 1000 # time in centi-seconds
    show_thinking = True

    # print name of chess engine
    print('Moonfish')

    stack = []
    while True:
        if stack:
            smove = stack.pop()
        else: smove = input()
        
        if smove == 'quit':
            break

        elif smove == 'ucci':
            print('ucciok')

        elif smove == 'isready':
            print('readyok')

        elif smove == 'newgame':
            stack.append('position fen ' + tools.FEN_INITIAL)

        elif smove.startswith('position'):
            params = smove.split(' ', 2)
            if params[1] == 'fen':
                fen = params[2]
                pos = tools.parseFEN(fen)
                color = RED if fen.split()[1] == 'w' else BLACK
            
        elif smove.startswith('go'):
            #  default options
            depth = 1000
            movetime = -1

            # parse parameters
            params = smove.split(' ')
            if len(params) == 1: continue

            i = 0
            while i < len(params):
                param = params[i]
                if param == 'depth':
                    i += 1
                    depth = int(params[i])
                if param == 'movetime':
                    i += 1
                    movetime = int(params[i])
                i += 1

            forced = False

            moves_remain = 40

            start = time.time()
            ponder = None
            for s_score in searcher._search(pos):
                moves = tools.pv(searcher, pos, include_scores=False)

                if show_thinking:
                    entry = searcher.tp_score.get((pos, searcher.depth, True))
                    score = int(round((entry.lower + entry.upper)/2))
                    usedtime = int((time.time() - start) * 1000)
                    moves_str = moves #if len(moves) < 15 else ''
                    print('info depth {} score {} time {} nodes {} pv {}'.format(searcher.depth, score, usedtime, searcher.nodes, moves_str))

                if len(moves) > 5:
                    ponder = moves[1]
                
                #将军死和被将军死 才会出现MATE_UPPER的值
                if (s_score >= MATE_UPPER) or (s_score <= -MATE_UPPER): 
                   break
            
                if movetime > 0 and (time.time() - start) * 1000 > movetime:
                    break

                if searcher.depth >= depth:
                    break

            entry = searcher.tp_score.get((pos, searcher.depth, True))
            m, s = searcher.tp_move.get(pos), entry.lower
            # We only resign once we are mated.. That's never?
            if s == -MATE_UPPER:
                print('resign')
            else:
                moves = moves.split(' ')
                if len(moves) > 1:
                    print('bestmove ' + moves[0] + ' ponder ' + moves[1])
                else:
                    print('bestmove ' + moves[0])

        elif smove.startswith('time'):
            our_time = int(smove.split()[1])

        elif smove.startswith('otim'):
            opp_time = int(smove.split()[1])

        else:
            pass

if __name__ == '__main__':
    main()
