import argparse
import sys
from threading import Thread
from time import sleep
from itertools import cycle
from multiprocessing import Pool, Process, freeze_context
import subprocess

from ThreadWriter import ThreadWriter
from Evaluator import Evaluator

import chess
import chess.engine


def lineCount(filename):
    try:
        with open(filename, 'r') as fin:
            l = len(fin.readlines())
    except FileNotFoundError:
        l = 0
    return l

def evalFENThread(output, i, fen, engine, d):
    board = chess.Board(fen)
    info = engine.analyse(board, chess.engine.Limit(depth=d))
    output[i] = str(info["score"].white()) + '\n'

def main(filein, fileout, d, threads, linetostart, enginepath):
    tw = ThreadWriter(fileout, threads, linetostart, lineCount(filein))
    thread_listener = Process(target=tw.listen)
    thread_listener.start()

    engine = Evaluator(enginepath)

    with open(filein, 'r') as fin:
        contents = (f[:-1] for f in fin.readlines()[linetostart:])

    try:
        with Pool(threads) as p:
            p.map(engine, zip(contents, cycle(range(threads))))
        sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        tw.terminate()
        engine.close()

if __name__ == "__main__":
    freeze_context()

    parser = argparse.ArgumentParser(description="Evaluate many many chess positions")
    parser.add_argument("-s", help="Source file with fens")
    parser.add_argument("-d", help="Destination evaluation file")
    parser.add_argument("-t", help="Number of threads to use", default=5)
    parser.add_argument("-e", help="Path to chess engine", default="stockfish")
    args = parser.parse_args()
    main(args.s, args.d, 22, int(args.t), lineCount(args.d), args.e)

