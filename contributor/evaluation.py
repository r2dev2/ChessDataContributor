import re

import chess
import chess.engine


class Evaluator:
    """
    Serializeable stockfish wrapper

    Example usage:
    >>> engine = Evaluator("stockfish")
    >>> engine("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    >>> del engine
    """
    depth = 20

    number_pattern = re.compile(r"\d+\.")
    def __init__(self, enginepath = "stockfish"):
        self._engine = chess.engine.SimpleEngine.popen_uci(enginepath)
        self._engine.configure({"Use NNUE": False})
        self._enginepath = enginepath

    def close(self):
        self._engine.close()

    def __call__(self, fen):
        """
        Evaluates the position.

        :param fen: the fen of the position
        :return: a tuple of (fen, evaluation, best move)
        """
        try:
            board = chess.Board(fen)
            info = self._engine.analyse(board, chess.engine.Limit(depth=Evaluator.depth))
            return self.__info_to_tuple(fen, info)
        except KeyboardInterrupt:
            pass

    @staticmethod
    def __info_to_tuple(fen, info):
        ev = str(info["score"].white())
        mov = str(info.get("pv", " ")[0]).strip()
        return fen, ev, mov

        # board = chess.Board(fen)
        # for move in info["pv"]:
        #     board.push(move)
        # san = chess.Board(fen).variation_san(board.move_stack)
        # filtered_san = ' '.join((
        #     m for m in san.split(' ')
        #     if re.match(Evaluator.number_pattern, m) is None
        # ))

        # return fen, ev, filtered_san

    def __getstate__(self):
        return (self._enginepath,)

    def __setstate__(self, state):
        self.__init__(*state)

    def __del__(self):
        self.close()


if __name__ == "__main__":
    engine = Evaluator("stockfish")
    print("Eval:", engine("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"))

