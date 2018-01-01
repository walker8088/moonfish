#!/usr/bin/env pypy
# -*- coding: utf-8 -*-
from __future__ import print_function
import moonfish
import re, sys, time

from itertools import count

###############################################################################
def load_pad_table(file):
    with open(file, 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
    index = 0    
    while True:
        if index >= len(lines):
            return True
        piece = lines[index].strip()        
        if piece not in pst:
            print("load pad table error at %d %s" % (index+1, piece))
            return False
        table = pst[piece]    
        for i in range(10):
            values = [int(x) for x in lines[index+i+1].strip().split()]
            for j in range(9):
                table[(i+3)*16+j+3] = values[j]
            #print(values)
            #print(table[(i+3)*16:(i+4)*16])            
        index += 11
    return True
    
def load_from_qcb(qcb_file):
        with open(qcb_file) as f:
            lines = f.readlines()
        
        books = []
        
        for line in lines:
            if line.startswith("*") :
                continue
            items = line.strip()
            books.append(items)
        
        return books    
###############################################################################

def move_to_zh(board, move):
    piece = board[move[0]]
    i, j = move
    move_from = (i // LINE_WITH - TOP, i % LINE_WITH - LEFT)
    move_to   = (j // LINE_WITH - TOP, j % LINE_WITH - LEFT)
    color = 0 if board[i].isupper() else 1
    #rank, fil = divmod(i - A1, LINE_WITH)
    
    diff = (move_to[0]-move_from[0], move_to[1]-move_from[1])
    base = h_level_index[color][move_from[1]]
    
    if diff[0] == 0:
        change_type = u'平'  
    elif diff[0] < 0:
        change_type = u'进' 
    else:
        change_type = u'退'
    
    if piece in 'NAB': 
        change = h_level_index[color][move_to[1]]
    else:
        change = h_level_index[color][move_to[1]] if (diff[0] == 0) else v_change_index[color][diff[0] if diff[0] > 0 else -diff[0]]
       
    return uni_pieces[piece.lower() if color == BLACK else piece] + base + change_type + change
    
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
    
###############################################################################

        
def iccs2internal(c):
    fil, rank = ord(c[0]) - ord('a'), int(c[1])
    return A0 + fil - LINE_WITH*rank

def internal2iccs(i):
    rank, fil = divmod(i - A0, LINE_WITH)
    return chr(fil + ord('a')) + str(-rank)

def render2(move, color):
    i,j = rotate_move(move) if color == BLACK else move
    return (internal2iccs(i)+internal2iccs(j))

def rotate_move(move):
    return(181 - move[0], 181 - move[1])

def in_king_house(pos):
    v_index = pos // LINE_WITH - TOP
    h_index = pos % LINE_WITH - LEFT
    if (v_index < 7) or (v_index > 9) : return False 
    if (h_index < 3) or (h_index > 5) : return False 
    return True
        

###############################################################################
# User interface
###############################################################################

###############################################################################
def do_game(fen):

    #load_pad_table('pad_table.txt')
    #pos = Position(board_initial, RED, 0)
    #pos = fen_to_pos('1C1a5/4k4/3a5/4N4/9/5R3/7r1/5p3/4p4/5K3 w')
    #pos = fen_to_pos('1C3k3/3C2P2/b1N1b4/4p4/9/7r1/R5n2/3n5/2p1p4/3K5 w') #Failed
    checker = RuleChecker()
    
    print(fen)
    pos = fen_to_pos(fen)
    
    searcher = Searcher()
    print_pos(pos)
    
    while True:
        
        '''
        if pos.is_checked():
            print(u'红方' if pos.move_color else '黑方', "将军!")
            if pos.is_dead():
                print(u'黑方' if pos.move_color else '红方', "被将死!")
                break
        # We query the user until she enters a (pseudo) legal move.
        #for move in pos.gen_moves():
            #print("%s %X:%X" % (pos.board[move[0]], move[0], move[1]))
        #    print(move_to_zh(pos.board, move))        
        
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
        print(move_to_zh(pos.board, move))        
        pos = pos.move(move)
        # After our move we rotate the board and print it again.
        # This allows us to see the effect of our move.
        print_pos(pos.rotate_board())
         
        if pos.is_checked():
            print(u'红方' if pos.move_color else '黑方', "将军!")
            if pos.is_dead():
                print(u'黑方' if pos.move_color else '红方', "被将死!")
                break
                
        if pos.score <= -MATE_LOWER:
            print(u"你赢了")
            break
        '''
        
        # Fire up the engine to look for a move.
        ban = checker.check_ban_move(pos)
        if ban : 
           print(ban) 
           return 0
        
        move, score, depth = searcher.search(pos, max_depth = 12, ban_move = ban) #,secs=30 )
        checker.append_move(pos, move)     
        print("Move: %s(%s) score: %d depth: %d" % (render2(move, pos.move_color), move_to_zh(pos.board, move), score, depth))
         
        pos = pos.move(move)
        
        if pos.move_color == RED:
            print_pos(pos)
        else:
            print_pos(pos.rotate_board())
        
        checked, dead = pos.is_checked_dead()
        if dead:
           print(u'黑方' if pos.move_color else '红方', "被将死!")
           return pos.move_color
        elif checked:
           print(u'红方' if pos.move_color else '黑方', "将军!") 
           
def main():
    bad_games = []
    books = load_from_qcb('end_games.qcb')
    #books = load_from_qcb('hard_game.txt')
    for i, fen in enumerate(books[1636:]):
        try:
            ret = do_game(fen)
            print(i+1)
            if ret == RED:
                bad_games.append(fen)
                break
        except Exception as e:
            print(e)
            time.sleep(3)
            break                
    with open('bad_games.txt', 'a+') as f:
        f.writelines(bad_games)
        
if __name__ == '__main__':
    main()

