import itertools as it
import os
import sys
from multiprocessing import freeze_support
from pathlib import Path
from queue import Queue
from threading import Event, Lock, Thread

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
    busy = [Event() for _ in range(threads)]
    for t in range(threads):
        busy[t].set()
        needs_q.put(t)
    manager = Manager()
    manager.init(args.input, args.input + ".progress")
    output_mutex = Lock()

    counterr = it.count()

    fense = set()
    for i, fen in enumerate(manager, 1):
        evrid = needs_q.get()
        def task(i, evrid, fen):
            try:
                assert busy[evrid].is_set()
                busy[evrid].clear()
                info = evaluators[evrid](fen)
                busy[evrid].set()
                needs_q.put(evrid)
                with output_mutex:
                    with open(args.output, 'a+') as fout:
                        print(*info, sep=',', file=fout)
                manager.mark_done(fen)
                next(counterr)
            except Exception:
                print("Error analysing %d with evaluators[%d]" % (i, evrid))

        assert fen not in fense
        fense.add(fen)
        Thread(target=task, args=(i, evrid, fen)).start()
        print(manager.last + 1, "/", len(manager), end='\r')

    for sem in busy:
        sem.wait()
    
    print()
    print(len(fense), next(counterr))

    del evaluators


if __name__ == "__main__":
    freeze_support()
    if "--cli" in sys.argv:
        sys.argv.remove("--cli")
    else:
        main = Gooey(main)
    main()
