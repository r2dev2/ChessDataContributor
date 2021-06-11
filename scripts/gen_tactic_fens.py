"""
Generate unique fens from a lichess puzzle database.

Usage:

>>> cat evals1.csv evals2.csv ... | python gen_tactic_fens.py lichess_puzzle_db.csv
"""

import itertools as it
import random as rng
import sys
from typing import NamedTuple, Iterable

import chess

from gen_fens import pos_from_fen, fens_from_stream

rng.seed(420)
blacklist = set()


class Puzzle(NamedTuple):
    fen: str
    moves: str
    rating: int

    def from_line(line: str) -> "Puzzle":
        f, m, r = line.split(",")[1:4]
        return Puzzle(f, m, int(r))

    def get_positions(self) -> Iterable[str]:
        board = chess.Board(self.fen)
        for move in self.moves.split(" "):
            board.push_uci(move)
            fen = pos_from_fen(board.fen())
            if fen in blacklist:
                continue
            blacklist.add(fen)
            yield board.fen()


def get_tactics(stream):
    puzzles = [*map(Puzzle.from_line, stream)]
    rng.shuffle(puzzles)
    ez = [p for p in puzzles if 600 <= p.rating <= 1300]
    mi = [p for p in puzzles if 1300 < p.rating <= 1900]
    ha = [p for p in puzzles if 1900 < p.rating <= 3000]
    amount = min(map(len, [ez, mi, ha]))
    return [*ez[:amount], *mi[:amount], *ha[:amount]]


def main(tactics_file):
    blacklist.update(fens_from_stream(sys.stdin))

    with open(tactics_file, "r") as fin:
        tactics = get_tactics(fin)

    positions = []
    for tactic in tactics:
        positions.extend(tactic.get_positions())
        print("Positions: ", len(positions), end="\r", flush=True)
    print()

    with open("tactic_positions.txt", "w+") as fout:
        print(*positions, file=fout, sep="\n")


if __name__ == "__main__":
    main(sys.argv[1])
