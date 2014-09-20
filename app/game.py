
class CellState(object):
    EMPTY = 0
    WHITE = 1
    BLACK = 2
    POSSIBLE_MOVE = 3


class Game(object):
    DEFAULT_POSITION = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 3, 0, 0, 0, 0],
        [0, 0, 3, 1, 2, 0, 0, 0],
        [0, 0, 0, 2, 1, 3, 0, 0],
        [0, 0, 0, 0, 3, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    def __init__(self, conn):
        self.conn = conn
        self.position = Game.DEFAULT_POSITION

    def send_position_changed(self):
        self.conn.send_message('position_changed', {
            'position': self.position
        })

    def on_game_started(self, data):
        self.position = Game.DEFAULT_POSITION
        self.send_position_changed()

    def on_move(self, data):
        self.position[data['a']][data['b']] = CellState.BLACK
        self.send_position_changed()
