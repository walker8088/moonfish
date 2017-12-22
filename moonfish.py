#!/usr/bin/env pypy
# -*- coding: utf-8 -*-
from __future__ import print_function
import re, sys, time
from itertools import count
from collections import OrderedDict, namedtuple

###############################################################################
# Piece-Square tables. 
###############################################################################

TOP = 3
BUTTOM = 12
LEFT = 3
RIGHT = 11

RED, BLACK = range(2)
        
piece = { 'P': 40, 'C':90, 'N':80, 'R': 190, 'A': 30, 'B':30, 'K': 10000 }

#pst from http://chinesechess.googlecode.com which is dead 
pst = {
    'P':(0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  9,  9,  9, 11, 13, 11,  9,  9,  9,  0,  0,  0,  0,
        0,  0,  0, 19, 24, 34, 42, 44, 42, 34, 24, 19,  0,  0,  0,  0,
        0,  0,  0, 19, 24, 32, 37, 37, 37, 32, 24, 19,  0,  0,  0,  0,
        0,  0,  0, 19, 23, 27, 29, 30, 29, 27, 23, 19,  0,  0,  0,  0,
        0,  0,  0, 14, 18, 20, 27, 29, 27, 20, 18, 14,  0,  0,  0,  0,
        0,  0,  0,  7,  0, 13,  0, 16,  0, 13,  0,  7,  0,  0,  0,  0,
        0,  0,  0,  7,  0,  7,  0, 15,  0,  7,  0,  7,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0),
          
    'K':(0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  1,  1,  1,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  2,  2,  2,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0, 11, 15, 11,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0),
        
     'A':(0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0, 20,  0, 20,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0, 23,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0, 20,  0, 20,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0),
        
    'B':(0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0, 20,  0,  0,  0, 20,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0, 18,  0,  0,  0, 23,  0,  0,  0, 18,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0, 23,  0,  0,  0, 23,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0),
        
    'N':(0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0, 90, 90, 90, 96, 90, 96, 90, 90, 90,  0,  0,  0,  0,
        0,  0,  0, 90, 96,103, 97, 94, 97,103, 96, 90,  0,  0,  0,  0,
        0,  0,  0, 92, 98, 99,103, 99,103, 99, 98, 92,  0,  0,  0,  0,
        0,  0,  0, 93,108,100,107,100,107,100,108, 93,  0,  0,  0,  0,
        0,  0,  0, 90,100, 99,103,104,103, 99,100, 90,  0,  0,  0,  0,
        0,  0,  0, 90, 98,101,102,103,102,101, 98, 90,  0,  0,  0,  0,
        0,  0,  0, 92, 94, 98, 95, 98, 95, 98, 94, 92,  0,  0,  0,  0,
        0,  0,  0, 93, 92, 94, 95, 92, 95, 94, 92, 93,  0,  0,  0,  0,
        0,  0,  0, 85, 90, 92, 93, 78, 93, 92, 90, 85,  0,  0,  0,  0,
        0,  0,  0, 88, 85, 90, 88, 90, 88, 90, 85, 88,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0),
        
    'R':(0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,206,208,207,213,214,213,207,208,206,  0,  0,  0,  0,
        0,  0,  0,206,212,209,216,233,216,209,212,206,  0,  0,  0,  0,
        0,  0,  0,206,208,207,214,216,214,207,208,206,  0,  0,  0,  0,
        0,  0,  0,206,213,213,216,216,216,213,213,206,  0,  0,  0,  0,
        0,  0,  0,208,211,211,214,215,214,211,211,208,  0,  0,  0,  0,
        0,  0,  0,208,212,212,214,215,214,212,212,208,  0,  0,  0,  0,
        0,  0,  0,204,209,204,212,214,212,204,209,204,  0,  0,  0,  0,
        0,  0,  0,198,208,204,212,212,212,204,208,198,  0,  0,  0,  0,
        0,  0,  0,200,208,206,212,200,212,206,208,200,  0,  0,  0,  0,
        0,  0,  0,194,206,204,212,200,212,204,206,194,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0),
        
    'C':(0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,100,100, 96, 91, 90, 91, 96,100,100,  0,  0,  0,  0,
        0,  0,  0, 98, 98, 96, 92, 89, 92, 96, 98, 98,  0,  0,  0,  0,
        0,  0,  0, 97, 97, 96, 91, 92, 91, 96, 97, 97,  0,  0,  0,  0,
        0,  0,  0, 96, 99, 99, 98,100, 98, 99, 99, 96,  0,  0,  0,  0,
        0,  0,  0, 96, 96, 96, 96,100, 96, 96, 96, 96,  0,  0,  0,  0,
        0,  0,  0, 95, 96, 99, 96,100, 96, 99, 96, 95,  0,  0,  0,  0,
        0,  0,  0, 96, 96, 96, 96, 96, 96, 96, 96, 96,  0,  0,  0,  0,
        0,  0,  0, 97, 96,100, 99,101, 99,100, 96, 97,  0,  0,  0,  0,
        0,  0,  0, 96, 97, 98, 98, 98, 98, 98, 97, 96,  0,  0,  0,  0,
        0,  0,  0, 96, 96, 97, 99, 99, 99, 97, 96, 96,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0),
}        
# Pad tables and join piece and pst dictionaries
'''
for k, table in pst.items():
    padrow = lambda row: (0,) + tuple(x+piece[k] for x in row) + (0,)
    pst[k] = sum((padrow(table[i*16:i*16+16]) for i in range(16)), ())
    pst[k] = (0,)*20 + pst[k] + (0,)*20
'''    
###############################################################################
# Global constants
###############################################################################

# Our board is represented as a 256 character string. The padding allows for
# fast detection of moves that don't stay within the board.
A1, I1 = 0xC3, 0xCC
initial = (
    '               \n'  #   0 - 0F
    '               \n'  #  10 - 1F
    '               \n'  #  20 - 2F
    '   rnbakabnr   \n'  #  30 - 3F
    '   .........   \n'  #  40 - 4F
    '   .c.....c.   \n'  #  50 - 5F
    '   p.p.p.p.p   \n'  #  60 - 6F
    '   .........   \n'  #  70 - 7F 
    '   .........   \n'  #  80 - 8F
    '   P.P.P.P.P   \n'  #  90 - 9F
    '   .C.....C.   \n'  #  A0 - AF
    '   .........   \n'  #  B0 - BF
    '   RNBAKABNR   \n'  #  C0 - CF
    '               \n'  #  D0 - DF
    '               \n'  #  E0 - EF
    '               \n'  #  F0 - FF
)

# Lists of possible moves for each piece type.

P_PRE_MOVES = (-0x10, -1, 1)
K_PRE_MOVES = (-0x10, 0x10, -1, 1)
A_PRE_MOVES = (-0x11, -0x0f, 0x11, 0x0f)
B_PRE_MOVES = ((-0x1E,-0x0F), (-0x22, -0x17), (0x1E, 0x0F), (0x22, 0x11))
N_PRE_MOVES = ((-0x21,-0x10), (-0x1F,-0x10), (-0x12,-1), (-0x0E, 1), (0x0E, -1), (0x12, 1), (0x1F,0x10), (0x21, 0x10))
DIRECTIONS = (0x10, 1, -0x10, -1)

# When a MATE is detected, we'll set the score to MATE_UPPER - plies to get there
# E.g. Mate in 3 will be MATE_UPPER - 6
MATE_LOWER = piece['K'] - 2 * (piece['R'] + piece['C'] + piece['N'] + piece['A'] + piece['B']) - 5 * piece['P']
MATE_UPPER = piece['K'] + 2 * (piece['R'] + piece['C'] + piece['N'] + piece['A'] + piece['B']) + 5 * piece['P']

# The table size is the maximum number of elements in the transposition table.
TABLE_SIZE = 1e8

# Constants for tuning search
QS_LIMIT = 150
EVAL_ROUGHNESS = 20

###############################################################################
# Chess logic
###############################################################################
def valid_pos(i):
    v_index = i // 0x10 - TOP
    h_index = i % 0x10 - LEFT
    if (v_index < 0) or (v_index > 9) : return False 
    if (h_index < 0) or (h_index > 8) : return False 
    return True
    
def in_king_house(pos):
    v_index = pos // 0x10 - TOP
    h_index = pos % 0x10 - LEFT
    if (v_index < 7) or (v_index > 9) : return False 
    if (h_index < 3) or (h_index > 5) : return False 
    return True
    
class Position(namedtuple('Position', 'board move_color score')):
    """ A state of a chess game
    board -- a 256 char representation of the board
    move_color -- WHITE(0), BLACK(1)
    score -- the board evaluation
    """
    
    def gen_moves(self):
        # For each of our pieces, iterate through each possible 'ray' of moves,
        # as defined in the 'directions' map. The rays are broken e.g. by
        # captures or immediately in case of pieces such as knights.
        
        for i, p in enumerate(self.board):
            if not p.isupper(): continue
            
            if p == 'P':
                #print(hex(i), p)               
                for d in P_PRE_MOVES:
                   j = i+d
                   v_line = i // 0x10 - TOP
                   q = self.board[j]
                   if q.isspace() or q.isupper(): continue
                   yield(i,j)
                   if v_line > 4: break
            
            elif p == 'K':
                for d in K_PRE_MOVES:
                   j = i+d
                   q = self.board[j]
                   if q.isspace() or q.isupper(): continue
                   if not in_king_house(j): continue
                   yield(i,j)
                   
            elif p == 'A':
                for d in A_PRE_MOVES:
                   j = i+d
                   q = self.board[j]
                   if q.isspace() or q.isupper(): continue
                   if not in_king_house(j): continue
                   yield(i,j)
                
            elif p == 'B':
                for d, bd in B_PRE_MOVES:
                   j = i+d
                   q = self.board[j]
                   if q.isspace() or q.isupper(): continue
                   bq = self.board[i+bd]
                   if bq.isalpha(): continue
                   yield(i,j)
                        
            elif p == 'N':
                for d, bd in N_PRE_MOVES:
                   j = i+d
                   q = self.board[j]
                   if q.isspace() or q.isupper(): continue
                   bq = self.board[i+bd]
                   if bq.isalpha(): continue
                   yield(i,j)
              
            elif p == 'R':
                for d in DIRECTIONS:
                    for j in count(i+d, d):
                        q = self.board[j]
                        # Stay inside the board, and off friendly pieces
                        if q.isspace() or q.isupper(): break
                        yield (i, j)
                        if q.islower(): break
                        
            elif p == 'C':
                for d in DIRECTIONS:
                    passed_count = 0 
                    for j in count(i+d, d):
                        q = self.board[j]
                        # Stay inside the board
                        if q.isspace(): break
                        if (passed_count == 0) and (q == '.'):
                            yield (i, j)
                            continue                                
                        if (passed_count == 1) and q.islower():
                            yield (i, j)
                            break                            
                        if q.isalpha():
                            passed_count += 1
                                
            else:
                print('****************Error*****************')
                return
                    
    def rotate(self):
        ''' Rotates the board, preserving enpassant '''
        tmp_board = self.board[::-1].swapcase()
        board = ''
        for i in range(0x10):
            row = tmp_board[i * 0x10 : i * 0x10 + 0x10]
            new_row = row[1:] + row[0]
            board += new_row                    
        return Position(board, 1 - self.move_color, -self.score)
        #return Position(self.board[::-1].swapcase(), -self.score)
    
    def rotate_board(self):
        pos = self.rotate()
        return Position(pos.board, 1 - pos.move_color, pos.score)
        
    def move(self, move):
        i, j = move
        p, q = self.board[i], self.board[j]
        put = lambda board, i, p: board[:i] + p + board[i+1:]
        # Copy variables
        board = self.board
        score = self.score + self.value(move)
        #print('Move Score %d to %d' % (self.score, score))
        # Actual move
        board = put(board, j, board[i])
        board = put(board, i, '.')
        # We rotate the returned position, so it's ready for the next player
        return Position(board, self.move_color, score).rotate()

    def value(self, move):
        i, j = move
        p, q = self.board[i], self.board[j]
        # Actual move
        score = pst[p][j] - pst[p][i]
        # Capture
        if q.islower():
            score += piece[q.upper()]
        
        return score

###############################################################################
# Search logic
###############################################################################

# lower <= s(pos) <= upper
Entry = namedtuple('Entry', 'lower upper')

# The normal OrderedDict doesn't update the position of a key in the list,
# when the value is changed.
class LRUCache:
    '''Store items in the order the keys were last added'''
    def __init__(self, size):
        self.od = OrderedDict()
        self.size = size

    def get(self, key, default=None):
        try: self.od.move_to_end(key)
        except KeyError: return default
        return self.od[key]

    def __setitem__(self, key, value):
        try: del self.od[key]
        except KeyError:
            if len(self.od) == self.size:
                self.od.popitem(last=False)
        self.od[key] = value

class Searcher:
    def __init__(self):
        self.tp_score = LRUCache(TABLE_SIZE)
        self.tp_move = LRUCache(TABLE_SIZE)
        self.nodes = 0
        self.max_depth = 100
        
    def bound(self, pos, gamma, depth, root=True):
        """ returns r where
                s(pos) <= r < gamma    if gamma > s(pos)
                gamma <= r <= s(pos)   if gamma <= s(pos)"""
        self.nodes += 1

        # Depth <= 0 is QSearch. Here any position is searched as deeply as is needed for calmness, and so there is no reason to keep different depths in the transposition table.
        depth = max(depth, 0)

        # We should always check if we
        # still have a king. Notice since this is the only termination check,
        # the remaining code has to be comfortable with being mated, stalemated
        # or able to capture the opponent king.
        if pos.score <= -MATE_LOWER:
            return -MATE_UPPER

        # Look in the table if we have already searched this position before.
        # We also need to be sure, that the stored search was over the same
        # nodes as the current search.
        entry = self.tp_score.get((pos, depth, root), Entry(-MATE_UPPER, MATE_UPPER))
        if entry.lower >= gamma and (not root or self.tp_move.get(pos) is not None):
            return entry.lower
        if entry.upper < gamma:
            return entry.upper

        # Here extensions may be added
        # Such as 'if in_check: depth += 1'

        # Generator of moves to search in order.
        # This allows us to define the moves, but only calculate them if needed.
        def moves():
            # First try not moving at all
            if depth > 0 and not root and any(c in pos.board for c in 'RBN'):
                yield None, -self.bound(pos.rotate(), 1-gamma, depth-3, root=False)
            # For QSearch we have a different kind of null-move
            if depth == 0:
                yield None, pos.score
            # Then killer move. We search it twice, but the tp will fix things for us. Note, we don't have to check for legality, since we've already done it before. Also note that in QS the killer must be a capture, otherwise we will be non deterministic.
            killer = self.tp_move.get(pos)
            if killer and (depth > 0 or pos.value(killer) >= QS_LIMIT):
                yield killer, -self.bound(pos.move(killer), 1-gamma, depth-1, root=False)
            # Then all the other moves
            for move in sorted(pos.gen_moves(), key=pos.value, reverse=True):
                if depth > 0 or pos.value(move) >= QS_LIMIT:
                    yield move, -self.bound(pos.move(move), 1-gamma, depth-1, root=False)

        # Run through the moves, shortcutting when possible
        best = -MATE_UPPER
        for move, score in moves():
            best = max(best, score)
            if best >= gamma:
                # Save the move for pv construction and killer heuristic
                self.tp_move[pos] = move
                break

        # Stalemate checking is a bit tricky: Say we failed low, because
        # we can't (legally) move and so the (real) score is -infty.
        # At the next depth we are allowed to just return r, -infty <= r < gamma,
        # which is normally fine.
        # However, what if gamma = -10 and we don't have any legal moves?
        # Then the score is actaully a draw and we should fail high!
        # Thus, if best < gamma and best < 0 we need to double check what we are doing.
        # This doesn't prevent sunfish from making a move that results in stalemate,
        # but only if depth == 1, so that's probably fair enough.
        # (Btw, at depth 1 we can also mate without realizing.)
        if best < gamma and best < 0 and depth > 0:
            is_dead = lambda pos: any(pos.value(m) >= MATE_LOWER for m in pos.gen_moves())
            if all(is_dead(pos.move(m)) for m in pos.gen_moves()):
                in_check = is_dead(pos.rotate())
                best = -MATE_UPPER if in_check else 0

        # Table part 2
        if best >= gamma:
            self.tp_score[(pos, depth, root)] = Entry(best, entry.upper)
        if best < gamma:
            self.tp_score[(pos, depth, root)] = Entry(entry.lower, best)

        return best

    def _search(self, pos):
        """ Iterative deepening MTD-bi search """
        self.nodes = 0

        # In finished games, we could potentially go far enough to cause a recursion
        # limit exception. Hence we bound the ply.
        for depth in range(1, self.max_depth):
            self.depth = depth
            # The inner loop is a binary search on the score of the position.
            # Inv: lower <= score <= upper
            # 'while lower != upper' would work, but play tests show a margin of 20 plays better.
            lower, upper = -MATE_UPPER, MATE_UPPER
            while lower < upper - EVAL_ROUGHNESS:
                gamma = (lower+upper+1)//2
                score = self.bound(pos, gamma, depth)
                print(depth, score, lower, upper)
                if score >= gamma:
                    lower = score
                if score < gamma:
                    upper = score
            # We want to make sure the move to play hasn't been kicked out of the table,
            # So we make another call that must always fail high and thus produce a move.
            score = self.bound(pos, lower, depth)
            print('%d Got Score %d\n'%(depth, score))
            # Yield so the user may inspect the search
            yield

    def search(self, pos, secs, max_depth = 12):
        self.max_depth = max_depth
        start = time.time()
        for _ in self._search(pos):
            if time.time() - start > secs:
                break
        # If the game hasn't finished we can retrieve our move from the
        # transposition table.
        return self.tp_move.get(pos), self.tp_score.get((pos, self.depth, True)).lower, self.depth


###############################################################################
# User interface
###############################################################################
# Python 2 compatability
if sys.version_info[0] == 2:
    input = raw_input
    class NewOrderedDict(OrderedDict):
        def move_to_end(self, key):
            value = self.pop(key)
            self[key] = value
    OrderedDict = NewOrderedDict
    
def iccs2internal(c):
    fil, rank = ord(c[0]) - ord('a'), int(c[1])
    return A1 + fil - 0x10*rank

def internal2iccs(i):
    rank, fil = divmod(i - A1, 0x10)
    return chr(fil + ord('a')) + str(-rank)

def render2(i,j):
    return (internal2iccs(i)+internal2iccs(j))

def rotate_move(move):
    return(0xFE - move[0], 0xFE - move[1])
    
uni_pieces = {
    'K': u"帅",
    'k': u"将",
    'A': u"仕",
    'a': u"士",
    'B': u"相",
    'b': u"象",
    'N': u"马",
    'n': u"碼",
    'R': u"车",
    'r': u"砗",
    'C': u"炮",
    'c': u"砲",
    'P': u"兵",
    'p': u"卒",
    '.': u' .',
}

def print_pos(pos):
    print()
    #print('     9  8  7  6  5  4  3  2  1')
    for i, row in enumerate(pos.board.split()):
        print('   %d'%(9-i), u' '.join(uni_pieces.get(p, p) for p in row))
        #print(' %X %d'%(i+3, 9-i), ' '.join(uni_pieces.get(p, p) for p in row))
        #print(' %X  '%(i+3), ' '.join(uni_pieces.get(p, p) for p in row))
    print('      a  b  c  d  e  f  g  h  i')
    #print('      3  4  5  6  7  8  9  A  B')
    print()
    print(u'   红方走' if pos.move_color == 0 else u'   黑方走')
    print()

def main():
    pos = Position(initial, RED, 0)
    searcher = Searcher()
    while True:
        print_pos(pos)
        
        if pos.score <= -MATE_LOWER:
            print(u"你输了")
            break

        # We query the user until she enters a (pseudo) legal move.
        #for move in pos.gen_moves():
        #    print("%s %X:%X" % (pos.board[move[0]], move[0], move[1]))
        move = None
        while move not in pos.gen_moves():
            match = re.match('([a-i][0-9])'*2, input('Your move: '))
            if match:
                move = iccs2internal(match.group(1)), iccs2internal(match.group(2))
                #print(hex(move[0]),hex(move[1]))
                #print(render2(*move))
            else:
                # Inform the user when invalid input (e.g. "help") is entered
                print("Please enter a move like h2e2")
                
        pos = pos.move(move)
        # After our move we rotate the board and print it again.
        # This allows us to see the effect of our move.
        print_pos(pos.rotate_board())
        
        if pos.score <= -MATE_LOWER:
            print(u"你赢了")
            break

        # Fire up the engine to look for a move.
        move, score, depth = searcher.search(pos, secs=7)
        if score == MATE_UPPER:
            print(u"将军!")

        # The black player moves from a rotated position, so we have to
        # 'back rotate' the move before printing it.
        real_move = rotate_move(move)
        print("My move: %s score: %d depth: %d" % (render2(*real_move), score, depth))
        pos = pos.move(move)
        
if __name__ == '__main__':
    main()

