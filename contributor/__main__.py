import os
import sys
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import freeze_support
from pathlib import Path
from queue import Queue
from threading import Lock, Thread

import chess
from gooey import Gooey, GooeyParser

import stockfish as sf
from manager import Manager
from evaluation import Evaluator


pwd = Path.cwd() / ".ChessContrib"


def main():
    parser = GooeyParser(description="Chess data contributor")
    parser.add_argument(
        "--threads",
        type=int,
        help="Number of threads to use",
        default=os.cpu_count(),
    )
    parser.add_argument(
        "--input",
        help="Name of input file",
        widget="FileChooser",
        required=True,
    )
    parser.add_argument(
        "--output",
        help="Name of output file",
        widget="FileSaver",
        required=True,
    )
    args = parser.parse_args()


    threads = int(args.threads)

    print("Using %d threads" % threads)

    sf.init()
    sfpath = sf.get_engine_path()

    print("Initialized stockfish")

    needs_q = Queue()
    evaluators = [Evaluator(sfpath) for _ in range(threads)]
    for t in range(threads):
        needs_q.put(t)
    manager = Manager()
    manager.init(args.input, args.input + ".progress")
    output_mutex = Lock()
    executor = ThreadPoolExecutor(max_workers=threads)

    for fen in manager:
        evrid = needs_q.get()
        def task():
            nonlocal evrid, fen, needs_q
            info = evaluators[evrid](fen)
            needs_q.put(evrid)
            with output_mutex:
                with open(args.output, 'a+') as fout:
                    print(*info, sep=',', file=fout)
            manager.mark_done(fen)

        executor.submit(task)

    del evaluators


if __name__ == "__main__":
    freeze_support()
    if "--cli" in sys.argv:
        sys.argv.remove("--cli")
    else:
        main = Gooey(main)
    main()
