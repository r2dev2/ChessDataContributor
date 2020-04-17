import argparse
import sys
from threading import Thread
import subprocess

import chess
import chess.engine

class threadWriter:
    def __init__(self, f):
        self.fout = open(f, 'a+')
        self.contents = ''
    def write(self, msg):
        self.contents += msg
    def close(self):
        self.fout.close()
        del self
    def flush(self):
        self.fout.write(self.contents)
        self.fout.flush()
    def read(self, no):
        pass
    def readlines(self):
        pass

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

def main(filein, fileout, d, threads, linetostart, enginepath, counterOutput = lambda x: print(x, end='\r', flush=True)):
    engines = [chess.engine.SimpleEngine.popen_uci(enginepath) for i in range(threads)]

    with open(filein, 'r') as fin:
        contents = fin.readlines()
    
    l = len(contents)
    contents = contents[linetostart:]
    
    counter = linetostart
    with open(fileout, 'a+') as fout:
        try:
            while counter < l:
                ts = []
                threadcontents = [0 for i in range(threads)]
                for i in range(threads):
                    try:
                        f = contents.pop(0)
                        fen = f[:-1]
                        t = Thread(
                            target = evalFENThread,
                            args = (threadcontents, i, fen, engines[i], d),
                            daemon = True
                        )
                        ts.append(t)
                    except IndexError:
                        print("Almost done")
                for t in ts:
                    t.start()
                for t in ts:
                    t.join()
                for c in threadcontents:
                    try:
                        fout.write(c)
                        fout.flush()
                    except:
                        if c != 0:
                            print("Add this:", c)
                counter += threads
                counterOutput(counter)
                del ts, threadcontents
        except KeyboardInterrupt:
            print()
            print("Caught Signal, beginning quit process")
            for t in ts:
                t.join()
            
    print("Done")
    for engine in engines: engine.quit()

# filein, fileout, d, threads, linetostart, enginepath
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Run with python evalfen.py -h to see help message")
        exit(0)
    parser = argparse.ArgumentParser(description="Evaluate many many chess positions")
    parser.add_argument("-s", help="Source file with fens")
    parser.add_argument("-d", help="Destination evaluation file")
    parser.add_argument("-t", help="Number of threads to use", default=5)
    parser.add_argument("-e", help="Path to chess engine", default="stockfish")
    args = parser.parse_args()
    main(args.s, args.d, 22, int(args.t), lineCount(args.d), args.e)

