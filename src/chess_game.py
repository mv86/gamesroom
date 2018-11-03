from src.game_enums import ChessPiece, Color, Direction
from src.game_errors import IllegalMoveError
from src.game import Coords, Game, move_direction

from src.game_pieces.bishop import Bishop
from src.game_pieces.king import King
from src.game_pieces.knight import Knight
from src.game_pieces.pawn import Pawn
from src.game_pieces.queen import Queen
from src.game_pieces.rook import Rook


class ChessGame(Game):
    """temp"""
    def __init__(self, restore_positions=None):
        super().__init__(
            board=[[None] * 8 for _ in range(8)],
            legal_piece_colors={Color.WHITE, Color.BLACK},
            legal_piece_names={piece.value for piece in ChessPiece},
            restore_positions=restore_positions
        )
        self.playing_color = Color.WHITE
        self.opponent_color = Color.BLACK

    @staticmethod
    def new_setup():
        """Return dictionary of new chess game default piece postitions.

        Dictionary is in following format:
        key = str representation of game coordinates xy
        value = chess GamePiece
        e.g '00': Rook(Color.WHITE)
        """
        white_pieces = chess_pieces(Color.WHITE, y_idxs=[0, 1])
        black_pieces = chess_pieces(Color.BLACK, y_idxs=[7, 6])
        return dict(white_pieces + black_pieces)

    def move(self, from_coords, to_coords):
        """temp"""
        self.validate_coords(from_coords, to_coords)
        self.set_move_attributes(from_coords, to_coords, self.playing_color)
        legal_move, make_move = self._move_type()

        if (legal_move(to_coords) and not self.own_king_in_check()
                and not self._piece_blocking(from_coords, to_coords)):
            make_move()
            if self._check_mate():
                self.winner = self.playing_color
                # TODO End game
            self._switch_players()
        else:
            raise IllegalMoveError('Illegal chess move attempted')

    def _move_type(self):
        if self._castle_move():
            return self._legal_castle, self._castle_move_type()
        if self._prawn_promotion():
            return self.playing_piece.legal_move, self._promote_pawn
        if self._capture_move():
            return self.playing_piece.legal_capture, self._capture
        return self.playing_piece.legal_move, self._move

    def _switch_players(self):
        playing_color = self.playing_color
        self.playing_color = self.opponent_color
        self.opponent_color = playing_color

    def _piece_blocking(self, from_coords, to_coords):
        """Check if any piece blocking move from_coords to_coords. Return bool."""
        if move_direction(from_coords, to_coords) != Direction.NON_LINEAR:
            # Only Knights move non_linear and they can jump over pieces
            for coords in self.coords_between(from_coords, to_coords):
                if self.board[coords.x][coords.y] is not None:
                    return True
        return False

    def _promote_pawn(self):
        self.board[self.from_coords.x][self.from_coords.y] = None
        # Defaults to Queen as most players want this
        # TODO Add functionality to choose promotion piece
        promoted_piece = Queen(self.playing_color)
        promoted_piece.coords = Coords(self.to_coords.x, self.to_coords.y)
        self.board[self.to_coords.x][self.to_coords.y] = promoted_piece

    def _move(self):
        self.board[self.from_coords.x][self.from_coords.y] = None
        self.playing_piece.coords = self.to_coords
        self.board[self.to_coords.x][self.to_coords.y] = self.playing_piece
        if self.playing_piece in [King(self.playing_color), Rook(self.playing_color)]:
            self.playing_piece.moved = True

    def _capture(self):
        captured_piece = self.board[self.to_coords.x][self.to_coords.y]
        captured_piece.coords = None
        self._move()

    def _castle_move(self):
        if self.playing_piece == King(Color.WHITE):
            if (self.from_coords == Coords(4, 0)
                    and self.to_coords in (Coords(2, 0), Coords(6, 0))):
                return True
        if self.playing_piece == King(Color.BLACK):
            if (self.from_coords == Coords(4, 7)
                    and self.to_coords in (Coords(2, 7), Coords(6, 7))):
                return True
        return False

    def _castle_move_type(self):
        if self._white_king_row():
            return self._white_castle()
        if self._black_king_row():
            return self._black_castle()

    def _white_king_row(self):
        return self.to_coords.y == 0

    def _black_king_row(self):
        return self.to_coords.y == 7

    def _king_side(self):
        return self.to_coords.x == 6

    def _queen_side(self):
        return self.to_coords.x == 2

    def _white_castle(self):
        if self._queen_side():
            return self._white_castle_queen_side
        return self._white_castle_king_side

    def _black_castle(self):
        if self._queen_side():
            return self._black_castle_queen_side
        return self._black_castle_king_side

    def _prawn_promotion(self):
        return (self.playing_piece == Pawn(Color.WHITE) and self.to_coords.y == 7
                or self.playing_piece == Pawn(Color.BLACK) and self.to_coords.y == 0)

    def _legal_castle(self, to_coords=None):
        playing_color = self.playing_color
        move_coords = self._castle_coords()

        if (self._king_moved(playing_color) or self._rook_moved(playing_color)
                or self._king_in_check(playing_color, self.from_coords)):
            return False

        for coords in move_coords:
            if (self.board[coords.x][coords.y] is not None
                    or self._king_in_check(playing_color, coords)):
                return False
        return True

    def _castle_coords(self):
        if self._white_king_row():
            if self._queen_side():
                castle_coords = (Coords(x=3, y=0), Coords(x=2, y=0))
            if self._king_side():
                castle_coords = (Coords(x=5, y=0), Coords(x=6, y=0))
        if self._black_king_row():
            if self._queen_side():
                castle_coords = (Coords(x=3, y=7), Coords(x=2, y=7))
            if self._king_side():
                castle_coords = (Coords(x=5, y=7), Coords(x=6, y=7))
        return castle_coords

    def _king(self, wanted_color):
        for row in self.board:
            for piece in row:
                if piece == King(wanted_color):
                    return piece

    def _king_moved(self, playing_color):
        king = self._king(playing_color)
        return king.moved

    def _rook_moved(self, playing_color):
        if playing_color == Color.WHITE:
            if self._king_side():
                piece = self.board[7][0]
            if self._queen_side():
                piece = self.board[0][0]

        if playing_color == Color.BLACK:
            if self._king_side():
                piece = self.board[7][7]
            if self._queen_side():
                piece = self.board[0][7]

        return piece and piece == Rook(playing_color) and piece.moved

    def _legal_en_passant(self):
        # check last move was opponent pawn moving 2 spaces
        pass

    def _white_castle_king_side(self):
        king, rook = self.board[4][0], self.board[7][0]
        self.board[4][0], self.board[7][0] = None, None
        self.board[6][0], self.board[5][0] = king, rook
        king.moved, rook.moved = True, True

    def _white_castle_queen_side(self):
        king, rook = self.board[4][0], self.board[0][0]
        self.board[4][0], self.board[0][0] = None, None
        self.board[2][0], self.board[3][0] = king, rook
        king.moved, rook.moved = True, True

    def _black_castle_king_side(self):
        king, rook = self.board[4][7], self.board[7][7]
        self.board[4][7], self.board[7][7] = None, None
        self.board[6][7], self.board[5][7] = king, rook
        king.moved, rook.moved = True, True

    def _black_castle_queen_side(self):
        king, rook = self.board[4][7], self.board[0][7]
        self.board[4][7], self.board[0][7] = None, None
        self.board[2][7], self.board[3][7] = king, rook
        king.moved, rook.moved = True, True

    def _capture_move(self):
        return self.board[self.to_coords.x][self.to_coords.y] is not None or self._en_passant()

    def _en_passant(self):
        piece = self.playing_piece
        # TODO Messy, needs a re-write
        if (piece == Pawn(self.playing_color) and piece.legal_capture(self.to_coords)
                and self.board[self.to_coords.x][self.to_coords.y] is None):
            if piece == Pawn(Color.WHITE) and self.to_coords.y == 5:
                return self.board[self.to_coords.x][self.to_coords.y - 1] == Pawn(Color.BLACK)
            if piece == Pawn(Color.BLACK) and self.to_coords.y == 2:
                return self.board[self.to_coords.x][self.to_coords.y + 1] == Pawn(Color.WHITE)
        return False

    def own_king_in_check(self):
        """Check if move puts current player king in check. Return bool."""
        # Keep track of current game state
        king = self._king(self.playing_color)
        original_king_coords = king.coords
        original_piece = self.board[self.to_coords.x][self.to_coords.y]

        # Temporarily change to future board position to see if it will lead to check
        self.board[self.from_coords.x][self.from_coords.y] = None
        self.board[self.to_coords.x][self.to_coords.y] = self.playing_piece
        if self.playing_piece == king:
            king.coords = self.to_coords

        # Perform check evaluation
        in_check = True if self._king_in_check(king.color, king.coords) else False

        # Return game to previous state
        self.board[self.from_coords.x][self.from_coords.y] = self.playing_piece
        self.board[self.to_coords.x][self.to_coords.y] = original_piece
        king.coords = original_king_coords

        return in_check

    def _check_mate(self):
        king = self._king(self.opponent_color)

        if not self._king_in_check(king.color, king.coords):
            return False
        if self._king_can_move_out_of_attack(king.coords):
            return False
        if self._can_attack_attacking_piece():
            return False
        if self._piece_can_block_attack(king.coords):
            return False
        return True

    def _king_in_check(self, king_color, king_coords):
        # king = self._king(color)
        opponent_color = Color.WHITE if king_color == Color.BLACK else Color.BLACK

        for piece in self._board_pieces(opponent_color):
            if (piece.legal_capture(king_coords)
                    and not self._piece_blocking(piece.coords, king_coords)):
                return True
        return False

    def _king_can_move_out_of_attack(self, king_coords):
        for square_coords in self._adjacent_empty_square_coords(king_coords):
            if not self._king_in_check(self.playing_color, square_coords):
                return True
        return False

    def _can_attack_attacking_piece(self):
        for piece in self._board_pieces(self.opponent_color):
            if (piece.legal_capture(self.to_coords)
                    and not self._piece_blocking(piece.coords, self.to_coords)):
                return True
        return False

    def _piece_can_block_attack(self, king_coords):
        pieces = self._board_pieces(self.opponent_color, king_wanted=False)
        for coords in self.coords_between(self.to_coords, king_coords):
            for piece in pieces:
                if (piece.legal_move(coords)
                        and not self._piece_blocking(piece.coords, coords)):
                    return True
        return False

    def _board_pieces(self, color, king_wanted=True):
        king = None if king_wanted else King(color)

        return [piece for row in self.board for piece in row
                if piece and piece.color == color and piece != king]

    def _adjacent_empty_square_coords(self, king_coords):
        adjacent_coords = {
            'N': lambda c: (c.x, c.y + 1),
            'NE': lambda c: (c.x + 1, c.y + 1),
            'E': lambda c: (c.x + 1, c.y),
            'SE': lambda c: (c.x + 1, c.y - 1),
            'S': lambda c: (c.x, c.y - 1),
            'SW': lambda c: (c.x - 1, c.y - 1),
            'W': lambda c: (c.x - 1, c.y),
            'NW': lambda c: (c.x - 1, c.y + 1)
        }
        potential_coords = [adjacent_coord(king_coords)
                            for adjacent_coord in adjacent_coords.values()]

        return [Coords(x, y) for x, y in potential_coords
                if self.coords_on_board(x, y) and self.board[x][y] is None]


def chess_pieces(color, *, y_idxs=None):
    """Helper method for new_chess_setup."""
    coords = [f'{x_idx}{y_idx}' for y_idx in y_idxs for x_idx in range(8)]
    pieces = [
        Rook(color),
        Knight(color),
        Bishop(color),
        Queen(color),
        King(color),
        Bishop(color),
        Knight(color),
        Rook(color),
        Pawn(color),
        Pawn(color),
        Pawn(color),
        Pawn(color),
        Pawn(color),
        Pawn(color),
        Pawn(color),
        Pawn(color)
    ]
    return list(zip(coords, pieces))
