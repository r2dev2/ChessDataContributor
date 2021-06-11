"""
Generate unique fens from lichess games database.

Usage:
>>> cat evals1.csv evals2.csv ... | python gen_fens.py lichess_games_db.csv
"""

import itertools as it
import sys

import chess
import chess.pgn

def get_games(path):
    try:
        with open(path, "r") as fin:
            for i in it.count():
                game = chess.pgn.read_game(fin)
                if game is None:
                    return
                yield game
    finally:
        print()


def extract_positions(game, blacklist, after_position):
    board = game.board()
    for move in game.mainline_moves():
        board.push(move)
        for pos in it.filterfalse(blacklist, possible_positions(board.fen())):
            after_position(pos)
            yield pos


def possible_positions(fen):
    board = chess.Board(fen)
    for move in board.legal_moves:
        board.push(move)
        yield board.fen()
        board.pop()


def pos_from_fen(fen):
    return "".join(fen.split(" ")[:4])


def fen_set_blacklist(set_):
    return lambda fen: pos_from_fen(fen) in set_


def fen_set_after_pos(set_):
    return lambda fen: set_.add(pos_from_fen(fen))


def fens_from_stream(stream):
    for line in stream:
        fen = line.split(",")[0]
        yield pos_from_fen(fen)


def main(pgnpath, fens=[]):
    positions = []
    already_exist = set(fens)
    for game in get_games(pgnpath):
        if len(positions) > 1e6:
            break
        positions.extend(extract_positions(
            game,
            fen_set_blacklist(already_exist),
            fen_set_after_pos(already_exist)
        ))
        print("Positions: ", len(positions), end="\r", flush=True)
    print(len(positions))
    with open("random_moves.txt", "w+") as fout:
        print(*positions, file=fout, sep="\n")


if __name__ == "__main__":
    main(sys.argv[1], fens_from_stream(sys.stdin))
