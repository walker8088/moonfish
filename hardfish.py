#!/usr/bin/env pypy
# -*- coding: utf-8 -*-
from __future__ import print_function
from moonfish import *
           
def main():
    bad_games = []
    books = load_from_qcb('hard_game.txt')
    for fen in books:
        #try:
            ret = do_game(fen)
            if ret == RED:
                bad_games.append(fen)
                break
        #except Exception as e:
        #    print(e)
        #    time.sleep(3)
        #    break                
    #with open('bad_games.txt', 'a+') as f:
    #    f.writelines(bad_games)
    for it in bad_games:
        print(it)
        
if __name__ == '__main__':
    main()

