import os
from pathlib import Path

from common import countOutput
import locks

class ThreadWriter:
    """
    Writes evaluations to threads or listens then writes evaluations
    """
    def __init__(self, filename: str, threads: int, num: int = 0, total: int = 1):
        """
        Constructor
        """

        self.filename = filename
        self.threads = threads
        self.num = num
        self.total = total

        self.fout = open(filename, 'a+')
        self.evals = [[] for i in range(threads)]

    def progressOut(self):
        countOutput(self.num, self.total)

    def flush(self):
        """
        Writes the contents to file
        """
        assert all(len(l) for l in self.evals)
        contents = (l.pop(0) for l in self.evals)

        for e in contents:
            print(e, file=self.fout, flush=True)

    def add(self, evaluation: str, pos: int):
        """
        Adds the eval evaluation at pos and automatically flushes and prints
        """

        self.evals[pos].append(evaluation)
        try:
            self.flush()
        except AssertionError:
            pass

        self.num += 1
        if self.total < self.num:
            self.total += 1
        self.progressOut()

    def listen(self):
        try:
            while True:
                for match in filter(lambda s: ".evaluation" in s, os.listdir(Path(os.getcwd())/"cache")):
                    n = int(match[:-11])
                    if any(f"{n}eval.lock" in s for s in os.listdir("cache")):
                        continue
                    locks.create(Path(os.getcwd())/ "cache"/f"{n}thread.lock")
                    with open(Path(os.getcwd())/"cache"/match, 'r') as fin:
                        evaluation = fin.read()
                    locks.delete(Path(os.getcwd())/"cache"/match)
                    locks.delete(Path(os.getcwd())/"cache"/f"{n}thread.lock")
                    self.add(evaluation, n)
        except BrokenPipeError:
            pass

    def __getstate__(self):
        return self.filename, self.threads, self.num, self.total

    def __setstate__(self, state):
        self.__init__(*state)


# Should result in test.txt of 
# hey
# testing
# ho
# finish it
if __name__ == "__main__":
    t = ThreadWriter("test.txt", 2)
    t.add("hey", 0)
    t.add("ho", 0)
    t.add("testing", 1)
    print(t.evals)
    t.add("finish it", 1)
