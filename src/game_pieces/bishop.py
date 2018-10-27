"""Module for Bishop class."""
from src.game_enums import Direction
from src.game_pieces.game_piece import GamePiece
from src.game import move_direction


class Bishop(GamePiece):
    """Bishop chess game piece. Inherits from GamePiece."""
    def __init__(self, color):
        super().__init__()
        self.color = color

    def valid_move(self, to_coords):
        return self._valid(to_coords)

    def valid_capture(self, to_coords):
        return self._valid(to_coords)

    def _valid(self, to_coords):
        return move_direction(self.coords, to_coords) == Direction.DIAGONAL
