from copy import deepcopy


class PlayerSide(object):
    WHITE = 1
    BLACK = 2

    @classmethod
    def get_opposite(cls, side):
        if side == cls.WHITE:
            return cls.BLACK
        elif side == cls.BLACK:
            return cls.WHITE
        else:
            raise InvalidMoveError('Incorrect player side')


class CellState(object):
    EMPTY = 0
    WHITE = 1
    BLACK = 2
    POSSIBLE_MOVE = 3

    empty_states = (EMPTY, POSSIBLE_MOVE)


class InvalidMoveError(Exception):
    pass


class Board(object):
    DEFAULT_POSITION = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 2, 0, 0, 0],
        [0, 0, 0, 2, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    SIDE_AMOUNT = 8

    def __init__(self):
        self._position = deepcopy(Board.DEFAULT_POSITION)

    def is_valid_coords(self, x, y):
        return (0 <= x < Board.SIDE_AMOUNT) and (0 <= y < Board.SIDE_AMOUNT)

    def is_valid_move(self, side, x, y):
        if not self._position[x][y] in CellState.empty_states:
            return False

        if not self.is_valid_coords(x, y):
            return False

        pos = deepcopy(self._position)
        pos[x][y] = side
        opponent = PlayerSide.get_opposite(side)

        directions = [[0, 1], [1, 1], [1, 0], [1, -1],
                      [0, -1], [-1, -1], [-1, 0], [-1, 1]]
        tiles_to_flip = []

        for x_direction, y_direction in directions:
            _x, _y = x, y
            # first steps in the direction
            _x += x_direction
            _y += y_direction
            if self.is_valid_coords(_x, _y) and pos[_x][_y] == opponent:
                # There is a piece belonging to the other player
                # next to our piece.
                _x += x_direction
                _y += y_direction

                if not self.is_valid_coords(_x, _y):
                    continue

                while pos[_x][_y] == opponent:
                    _x += x_direction
                    _y += y_direction
                    if not self.is_valid_coords(_x, _y):
                        # break out of while loop, then continue in for loop
                        break

                if not self.is_valid_coords(_x, _y):
                    continue

                if pos[_x][_y] == side:
                    # There are pieces to flip over.
                    # Go in the reverse direction until we reach
                    # the original space, noting all the tiles along the way.
                    while True:
                        _x -= x_direction
                        _y -= y_direction
                        if _x == x and _y == y:
                            break
                        tiles_to_flip.append([_x, _y])

         # If no tiles were flipped, this is not a valid move.
        if len(tiles_to_flip) == 0:
            return False

        return tiles_to_flip

    def get_possible_moves_position(self, side):
        # Returns a position with the valid moves the given player can make.
        pos = deepcopy(self._position)
        for x, y in self.get_valid_moves(side):
            pos[x][y] = CellState.POSSIBLE_MOVE
        return pos

    def get_valid_moves(self, side):
        # Returns a list of [x,y] lists of valid moves
        # for the given player.
        valid_moves = []
        for x in range(Board.SIDE_AMOUNT):
            for y in range(Board.SIDE_AMOUNT):
                if self.is_valid_move(side, x, y):
                    valid_moves.append([x, y])
        return valid_moves

    def get_score(self):
        # Determine the score by counting the tiles.
        # Returns a dictionary with keys 'X' and 'O'.
        score = {
            PlayerSide.WHITE: 0,
            PlayerSide.BLACK: 0,
        }
        for x in range(Board.SIDE_AMOUNT):
            for y in range(Board.SIDE_AMOUNT):
                for side in score.keys():
                    if self._position[x][y] == side:
                        score[side] += 1
        return score

    def make_move(self, side, x, y):
        # Place the tile on the board at x, y, and flip
        # any of the opponent's pieces.
        if not side in (PlayerSide.WHITE, PlayerSide.BLACK):
            raise InvalidMoveError('Incorrect player side')

        if not self._position[x][y] in CellState.empty_states:
            raise InvalidMoveError('Cell is not empty')

        if not self.is_valid_coords(x, y):
            raise InvalidMoveError('Invalid cell coordinates')

        tiles_to_flip = self.is_valid_move(side, x, y)
        if not tiles_to_flip:
            raise InvalidMoveError("There's no tiles to flip")

        self._position[x][y] = side
        for _x, _y in tiles_to_flip:
            self._position[_x][_y] = side


class Game(object):
    def __init__(self, conn):
        self.conn = conn
        self.board = Board()

    def send_position_changed(self, side):
        self.conn.send_message('position_changed', {
            'position': self.board.get_possible_moves_position(side)
        })

    def on_game_started(self, data):
        self.board = Board()
        self.send_position_changed(PlayerSide.BLACK)

    def on_move(self, data):
        try:
            self.board.make_move(PlayerSide.BLACK, data['x'], data['y'])
        except InvalidMoveError as ex:
            # TODO: react
            print ex
        self.send_position_changed(PlayerSide.BLACK)
