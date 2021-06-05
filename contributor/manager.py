import itertools as it
from threading import Thread, Lock
from queue import Queue


class Manager(it.count):
    """
    Manages which fens to evaluate and is thread safe.

    Usage:
        >>> m = Manager()
        >>> m.init("path to fen file", "path to progress file")
        >>> for fen in m:
        >>>     evaluate(fen)
        >>>     m.mark_done(fen)
    """
    def init(self, fen_path, output_path):
        with open(fen_path, 'r') as fin:
            self._fens = [*map(str.strip, fin)]
        self._progress =  Progress(output_path)
        self.last = 0

    def mark_done(self, fen):
        self._progress.add(fen)

    def __len__(self):
        return len(self._fens)

    def __next__(self):
        try:
            res = super().__next__()
            while (self._fens[res] in self._progress):
                res = super().__next__()
            self.last = res
        except IndexError:
            raise StopIteration

        return self._fens[res]


class Progress(set):
    def __init__(self, output_file):
        super().__init__()
        try:
            with open(output_file, 'r') as fin:
                for line in fin:
                    super().add(line.split(",")[0].strip())
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    m = Manager()
    m.init("test_file.txt", "progress.txt")
    for fen in m:
        print(fen)
        if input("done? ") == 'y':
            m.mark_done(fen)
