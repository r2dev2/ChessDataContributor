from queue import Queue
from multiprocessing import freeze_support

import chess

import stockfish as sf
from manager import Manager
from evaluation import Evaluator


def main():
    threads = 5
    sf.init()
    sfpath = sf.get_engine_path()

    needs_q = Queue()
    evaluators = [Evaluator(sfpath) for _ in range(threads)]
    for t in range(threads):
        needs_q.put(t)


if __name__ == "__main__":
    freeze_support()
    main()
