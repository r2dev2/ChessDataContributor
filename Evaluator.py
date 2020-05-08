from multiprocessing import Queue, Pool, Array, Process
from itertools import cycle, repeat
from time import sleep
import os
from pathlib import Path
import sys

import chess
import chess.engine

import locks
from ThreadWriter import ThreadWriter

class Evaluator:
    """
    Stockfish wrapper

    Example usage:
    engine = Evaluator("stockfish")
    engine("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    """
    def __init__(self, enginepath: str = "stockfish"):
        self.engine = chess.engine.SimpleEngine.popen_uci(enginepath)
        self.enginepath = enginepath

    def close(self):
        self.engine.close()
        sleep(5)

    def __call__(self, args): #output, number=0):
        """
        Takes in fen, number
        """
        try:
            fen, number = args
            board = chess.Board(fen)
            info = self.engine.analyse(board, chess.engine.Limit(depth=22))
            result = str(number) + '\t' + str(info["score"].white())
            while any(f"{number}writer.lock" in s for s in os.listdir("cache")):
                pass
            locks.create(Path("cache") / f"{number}eval.lock")
            with open(Path("cache") / f"{number}.evaluation", 'a+') as fout:
                print(str(info["score"].white()), file=fout, end='')
            locks.delete(Path("cache") / f"{number}eval.lock")
        except KeyboardInterrupt:
            pass
        # print(result)

    def __getstate__(self):
        return (self.enginepath,)

    def __setstate__(self, state):
        self.__init__(*state)

if __name__ == "__main__":
    engine = Evaluator()
    fens = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
        "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2",
        "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"
    ]

    t = ThreadWriter("results.txt", 8)

    listener = Process(target=t.listen)
    listener.start()

    with Pool() as p:
        p.map(engine, zip(fens*4, cycle(range(8))))

    sleep(1)
    listener.terminate()

    engine.close()
    sys.exit(0)
