import itertools as it
from threading import Thread, Lock


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
    def init(self, fen_path, progress_path):
        with open(fen_path, 'r') as fin:
            self._fens = [line.rstrip().lstrip() for line in fin]
        self._progress =  Progress(progress_path)

    def mark_done(self, fen):
        self._progress.add(fen)

    def __next__(self):
        try:
            res = super().__next__()
            while (self._fens[res] in self._progress):
                res = super().__next__()
        except IndexError:
            raise StopIteration
        
        return self._fens[res]


class Progress(set):
    def __init__(self, progress_file):
        super().__init__()
        self._progress_file = progress_file
        self._mutex = Lock()
        try:
            with open(self._progress_file, 'r') as fin:
                for line in fin:
                    super().add(line.rstrip().lstrip())
        except FileNotFoundError:
            pass

    def add(self, n):
        super().add(n)
        self.save()

    def save(self):
        Thread(target=self.__save_task).start()

    def __save_task(self):
        with self._mutex:
            with open(self._progress_file, 'w+') as fout:
                print(*self, sep='\n', end='', file=fout)


if __name__ == "__main__":
    m = Manager()
    m.init("test_file.txt", "progress.txt")
    for fen in m:
        print(fen)
        if input("done? ") == 'y':
            m.mark_done(fen)
