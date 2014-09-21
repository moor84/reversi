from uuid import uuid1
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


class Player(object):
    def __init__(self, side, conn):
        self.id = str(uuid1().hex)  # Keep it secret for other player
        self.side = side
        self.conn = conn
        self.ip = conn.request.remote_ip


class Game(object):
    games = {}

    @classmethod
    def on_message(cls, message, conn):
        if message['event'] == 'start_new_game':
            cls.start_new_game(conn)
            return
        elif message['event'] == 'join_game':
            cls.join_game(conn)
            return
        game = cls.games.get(message['game_id'])
        if not game:
            # TODO: react
            return
        handler = getattr(game, 'on_' + message['event'])
        if handler:
            handler(message['data'])

    @classmethod
    def start_new_game(cls, conn):
        game = Game(conn)
        cls.games[game.id] = game
        conn.send_message('game_started', {
            'game_id': game.id,
            'player': {
                'id': game.default_player.id,
                'ip': game.default_player.ip
            }
        })

    @classmethod
    def join_game(cls, conn):
        game = None
        for game_id, _game in cls.games.items():
            if len(_game.players.keys()) == 1:
                game = _game
        if not game:
            print 'No game available'
            # TODO: react
            return
        # The whites're second
        player = Player(PlayerSide.WHITE, conn)
        game.players[player.id] = player
        conn.send_message('joined_game', {
            'game_id': game.id,
            'host_ip': game.default_player.ip,
            'player': {
                'id': player.id
            }
        })
        game.default_player.conn.send_message('player_joined_game', {
            'game_id': game.id,
            'player': {
                'ip': player.ip
            }
        })
        game.current_player = game.default_player
        game.send_position_changed()

    def __init__(self, conn):
        self.id = str(uuid1().hex)
        self.board = Board()
        # Player, who created the game (the blacks're first)
        self.default_player = Player(
            PlayerSide.BLACK, conn)
        self.players = {
            self.default_player.id: self.default_player,
        }
        # Player to move
        self.current_player = None

    def send_position_changed(self):
        score = self.board.get_score()
        for player_id, player in self.players.items():
            player.conn.send_message('position_changed', {
                'position': self.board.get_possible_moves_position(
                    player.side),
                'my_turn': (self.current_player == player),
                'my_score': score[player.side],
                'opponents_score': score[PlayerSide.get_opposite(player.side)]
            })

    def send_game_over(self):
        score = self.board.get_score()
        for player_id, player in self.players.items():
            my_score = score[player.side]
            opponents_score = score[PlayerSide.get_opposite(player.side)]
            player.conn.send_message('game_over', {
                'position': self.board.get_possible_moves_position(
                    player.side),
                'i_won': (my_score > opponents_score),
                'opponent_won': (opponents_score > my_score),
                'my_score': my_score,
                'opponents_score': opponents_score
            })
        del Game.games[self.id]

    def on_move(self, data):
        player_id = data['player_id']
        try:
            if not player_id or not player_id in self.players:
                raise InvalidMoveError('Incorrect player credentials')
            player = self.players[player_id]
            if self.current_player != player:
                raise InvalidMoveError("It's not this player's turn")
            self.board.make_move(player.side, data['x'], data['y'])

            opposite_side = PlayerSide.get_opposite(player.side)
            if not self.board.get_valid_moves(opposite_side):
                self.send_game_over()
                return

            # Change turns
            for _, _player in self.players.items():
                if _player != player:
                    self.current_player = _player
                    break

        except InvalidMoveError as ex:
            # TODO: react
            print ex
        self.send_position_changed()
