import itertools
import re

from moonfish import *

################################################################################
# This module contains functions used by test.py and xboard.py.
# Nothing from here is imported into moonfish.py which is entirely self-sufficient
################################################################################

FEN_INITIAL = 'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1'

################################################################################
# Parse and Render moves
################################################################################

def gen_legal_moves(pos):
    ''' pos.gen_moves(), but without those that leaves us in check.
        Also the position after moving is included. '''
    for move in pos.gen_moves():
        pos1 = pos.move(move)
        # If we just checked for opponent moves capturing the king, we would miss
        # captures in case of illegal castling.
        if not any(pos1.value(m) >= MATE_LOWER for m in pos1.gen_moves()):
            yield move, pos1

def mrender(pos, m):
    # Sunfish always assumes promotion to queen
    p = ''
    m = m if get_color(pos) == RED else (0xfE-m[0], 0xFE-m[1])
    return internal2iccs(m[0]) + internal2iccs(m[1]) + p

def mparse(color, move):
    m = (iccs2internal(move[0:2]), iccs2internal(move[2:4]))
    return m if color == RED else (0xfE--m[0], 0xfE--m[1])

def renderSAN(pos, move):
    ''' Assumes board is rotated to position of current player '''
    i, j = move
    csrc, cdst = render(i), render(j)
    # Rotate flor black
    if get_color(pos) == BLACK:
        csrc, cdst = render(119-i), render(119-j)
    # Check
    pos1 = pos.move(move)
    cankill = lambda p: any(p.board[b]=='k' for a,b in p.gen_moves())
    check = ''
    if cankill(pos1.rotate()):
        check = '+'
        if all(cankill(pos1.move(move1)) for move1 in pos1.gen_moves()):
            check = '#'
    # Castling
    if pos.board[i] == 'K' and abs(i-j) == 2:
        if get_color(pos) == RED and j > i or get_color(pos) == BLACK and j < i:
            return 'O-O' + check
        else:
            return 'O-O-O' + check
    # Pawn moves
    if pos.board[i] == 'P':
        pro = '=Q' if A8 <= j <= H8 else ''
        cap = csrc[0] + 'x' if pos.board[j] != '.' or j == pos.ep else ''
        return cap + cdst + pro + check
    # Figure out what files and ranks we need to include
    srcs = [a for (a,b),_ in gen_legal_moves(pos) if pos.board[a] == pos.board[i] and b == j]
    srcs_file = [a for a in srcs if (a - A1) % 10 == (i - A1) % 10]
    srcs_rank = [a for a in srcs if (a - A1) // 10 == (i - A1) // 10]
    assert srcs, 'No moves compatible with {}'.format(move)
    if len(srcs) == 1: src = ''
    elif len(srcs_file) == 1: src = csrc[0]
    elif len(srcs_rank) == 1: src = csrc[1]
    else: src = csrc
    # Normal moves
    p = pos.board[i]
    cap = 'x' if pos.board[j] != '.' else ''
    return p + src + cap + cdst + check

def parseSAN(pos, msan):
    ''' Assumes board is rotated to position of current player '''
    # Normal moves
    normal = re.match('([KQRBN])([a-h])?([1-8])?x?([a-h][1-8])', msan)
    if normal:
        p, fil, rank, dst = normal.groups()
        src = (fil or '[a-h]')+(rank or '[1-8]')
    # Pawn moves
    pawn = re.match('([a-h])?x?([a-h][1-8])', msan)
    if pawn:
        p, (fil, dst) = 'P', pawn.groups()
        src = (fil or '[a-h]')+'[1-8]'
    # Castling
    if re.match(msan, "O-O-O[+#]?"):
        p, src, dst = 'K', 'e[18]', 'c[18]'
    if re.match(msan, "O-O[+#]?"):
        p, src, dst = 'K', 'e[18]', 'g[18]'
    # Find possible match
    for (i, j), _ in gen_legal_moves(pos):
        if get_color(pos) == RED:
            csrc, cdst = render(i), render(j)
        else: csrc, cdst = render(119-i), render(119-j)
        if pos.board[i] == p and re.match(dst,cdst) and re.match(src,csrc):
            return (i, j)
    assert False

################################################################################
# Parse and Render positions
################################################################################

def get_color(pos):
    return pos.move_color

def parseFEN(fen):
    """ Parses a string in Forsyth-Edwards Notation into a Position """
    board, color, _, __, _hclock, _fclock = fen.split()
    board = re.sub(r'\d', (lambda m: '.'*int(m.group(0))), board)
    
    init_board = list(256*' ')
    init_board[15::16] = ['\n']*16
    for i, row in enumerate(board.split('/')):
        #print(row)
        for j, ch in enumerate(row):
            init_board[(i+3) * 16 + j+3] = ch
    init_board = ''.join(init_board)
    
    score = sum(pst[p][i] for i,p in enumerate(init_board) if p.isupper())
    score += sum(piece[p] for i,p in enumerate(init_board) if p.isupper())
    score -= sum(pst[p.upper()][0xFE - i] for i,p in enumerate(init_board) if p.islower())
    score -= sum(piece[p.upper()] for i,p in enumerate(init_board) if p.islower())
    
    #print(score)
    pos = Position(init_board, RED, score)
    return pos if color == 'w' else pos.rotate()

def renderFEN(pos, half_move_clock=0, full_move_clock=1):
    color = 'wb'[get_color(pos)]
    if get_color(pos) == BLACK:
        pos = pos.rotate()
    board = '/'.join(pos.board.split())
    board = re.sub(r'\.+', (lambda m: str(len(m.group(0)))), board)
    castling =  '-'
    ep = render(pos.ep) if not pos.board[pos.ep].isspace() else '-'
    clock = '{} {}'.format(half_move_clock, full_move_clock)
    return ' '.join((board, color, castling, ep, clock))


################################################################################
# Pretty print
################################################################################

def pv(searcher, pos, include_scores=True):
    res = []
    seen_pos = set()
    color = get_color(pos)
    origc = color
    if include_scores:
        res.append(str(pos.score))
    while True:
        move = searcher.tp_move.get(pos)
        if move is None:
            break
        res.append(mrender(pos, move))
        pos, color = pos.move(move), 1-color
        if pos in seen_pos:
            res.append('loop')
            break
        seen_pos.add(pos)
        if include_scores:
            res.append(str(pos.score if color==origc else -pos.score))
    return ' '.join(res)

################################################################################
# Bulk move generation
################################################################################

def expand_position(pos):
    ''' Yiels a tree of generators [p, [p, [...], ...], ...] rooted at pos '''
    yield pos
    for _, pos1 in gen_legal_moves(pos):
        yield expand_position(pos1)

def collect_tree_depth(tree, depth):
    ''' Yields positions exactly at depth '''
    root = next(tree)
    if depth == 0:
        yield root
    else:
        for subtree in tree:
            for pos in collect_tree_depth(subtree, depth-1):
                yield pos

def flatten_tree(tree, depth):
    ''' Yields positions exactly at less than depth '''
    if depth == 0:
        return
    yield next(tree)
    for subtree in tree:
        for pos in flatten_tree(subtree, depth-1):
            yield pos

