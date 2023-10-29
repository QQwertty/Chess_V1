import copy

class Piece():

    def __init__(self, color, piece_type, position, abbr):
        self.color = color
        self.piece_type = piece_type
        self.position = position
        self.abbr = abbr
        self.moves_made = 0

    def generate_moves(self, board, game):
        raise NotImplementedError("Subclasses must implement generate_moves")

    def is_legal_move(self, move, board, game):
        raise NotImplementedError("Subclasses must implement is_legal_move")
    
    def is_check(self, board, game):
        """
        Given the board, method checks if king is in check
        Used for castling
        """

        # Find all squares that are under attack
        is_check = False
        danger_squares = []
        for piece in board.values():
            if piece is not None and piece.color != self.color and piece.piece_type != "king":
                danger_moves = piece.generate_moves(board, game)

                danger_squares.extend(danger_moves)

        # If king is under attack return true
        for piece in board.values():
            if piece is not None:
                if piece.color == self.color and piece.piece_type == "king":
                    if piece.position in danger_squares:
                        is_check = True

        return is_check


class Pawn(Piece):
        def __init__(self, color, position):
            super().__init__(color, "pawn", position, "P")


        def generate_moves(self, board, game):
            moves = []
            row, column = self.position

            # White pawn can move down the board 1 square
            if self.color == "white" and row != 7:
                # If square ahead of pawn is empty, add to list
                if board[(row + 1, column)] is None:
                    moves.append((row + 1, column))

                # Allow pawns to take diagonally
                if column + 1 <= 7 and board[(row + 1, column + 1)] is not None and board[(row + 1, column + 1)].color == "black":
                    moves.append((row + 1, column + 1))

                # Allow pawns to take diagonally
                if column - 1 >= 0 and board[(row + 1, column - 1)] is not None and board[(row + 1, column - 1)].color == "black":
                    moves.append((row + 1, column - 1))

            # Black pawn can move up the board 1 square
            elif self.color == "black" and row != 0:
                # If square ahead of pawn is empty, add to list
                if board[(row - 1, column)] is None:
                    moves.append((row - 1, column))

                 # Allow pawns to take diagonally
                if column + 1 <= 7 and board[(row - 1, column + 1)] is not None and board[(row - 1, column + 1)].color == "white":
                    moves.append((row - 1, column + 1))

                 # Allow pawns to take diagonally
                if column - 1 >= 0 and board[(row - 1, column - 1)] is not None and board[(row - 1, column - 1)].color == "white":
                    moves.append((row - 1, column - 1))

            # Allow pawns to double move if it has not moved yet
            if self.moves_made == 0:
                if self.color == "white" and board[(row + 2, column)] is None and board[(row + 1, column)] is None:
                    moves.append((row + 2, column))
                elif self.color == "black" and board[(row - 2, column)] is None and board[(row - 1, column)] is None:
                    moves.append((row - 2, column))

            # Allow en passant
            if game.last_move is not None:
                if game.last_move[1] == 'P':
                    row, col = game.last_move[0]
                    row1, col1 = game.last_move[2]
                    # White pawn moved, Black pawn can take
                    if row1 - row == 2:
                        b_row, b_col = self.position
                        # If white pawn is to the left
                        if b_col > col1 and b_row == row1:
                            moves.append((b_row - 1, b_col - 1))
                        # If white pawn is to the right
                        elif b_col < col1 and b_row == row1:
                            moves.append((b_row - 1, b_col + 1))

                    # Black pawn moved, White pawn can take
                    elif row1 - row == -2:
                        w_row, w_col = self.position
                        # If black pawn is to the left
                        if w_col > col1 and w_row == row1:
                            moves.append((w_row + 1, w_col - 1))
                        # If black pawn is to the right
                        elif w_col < col1 and w_row == row1:
                            moves.append((w_row + 1, w_col + 1))

            return moves


        def is_legal_move(self, move, board, game):
            moves = self.generate_moves(board, game)
            # Create a temporary board 
            # Check if move takes king out of check or into check
            temp_board = copy.deepcopy(board)
            temp_board = game.make_move([self.position, self.abbr, move], temp_board)
            if self.is_check(temp_board, game):
                return False
            else:
                return move in moves


class Horse(Piece):

        def __init__(self, color, position):
            super().__init__(color, "horse", position, "H")

        def generate_moves(self, board, game):
            """ 
            Knight/Horse's Moves:
            """
            moves = []
            # Possible standard horse moves
            possible_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

            # Loop through possible moves
            # If destination is empty or an enemy piece, add move
            for i, j in possible_moves:
                row, column = self.position
                row += i
                column += j
                if 0 <= row < 8 and 0 <= column < 8 and (board[(row, column)] is None or board[(row, column)].color != self.color):
                    moves.append((row, column))

            return moves

        def is_legal_move(self, move, board, game):
            moves = self.generate_moves(board, game)
            # Create a temporary board 
            # Check if move takes king out of check or into check
            temp_board = copy.deepcopy(board)
            temp_board = game.make_move([self.position, self.abbr, move], temp_board)
            if self.is_check(temp_board, game):
                return False
            else:
                return move in moves


class Bishop(Piece):

        def __init__(self, color, position):
            super().__init__(color, "bishop", position, "B")

        def generate_moves(self, board, game):
            """Bishop's Moves:
            Check diagonal positions until an obstruction is encountered.
            If the obstruction is an opponent's piece, include it as a valid move (capture).
            """

            moves = []
            # Possible standard bishop moves
            possible_moves = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

            # Loop through possible moves until an enemy or boundry is found
            for i, j in possible_moves:
                row, column = self.position
                while True:
                    row += i
                    column += j
                    if 0 <= row < 8 and 0 <= column < 8:
                        if board[(row, column)] is not None:
                            if board[(row, column)].color != self.color:
                                moves.append((row, column))
                            break
                        else:
                            moves.append((row, column))
                    else:
                        break

            return moves

        def is_legal_move(self, move, board, game):
            moves = self.generate_moves(board, game)
            # Create a temporary board 
            # Check if move takes king out of check or into check
            temp_board = copy.deepcopy(board)
            temp_board = game.make_move([self.position, self.abbr, move], temp_board)
            if self.is_check(temp_board, game):
                return False
            else:
                return move in moves

class Rook(Piece):

        def __init__(self, color, position):
            super().__init__(color, "rook", position, "R")

        def generate_moves(self, board, game):
            """ Rook's Moves:
            Check column/row until an obstruction is encountered.
            If the obstruction is an opponent's piece, include it as a valid move (capture).
            """
            moves = []
            # Possible standard rook moves
            possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]

            # Loop through possible moves until an enemy or boundry is found
            for i, j in possible_moves:
                row, column = self.position
                while True:
                    row += i
                    column += j
                    if 0 <= row < 8 and 0 <= column < 8:
                        if board[(row, column)] is not None:
                            if board[(row, column)].color != self.color:
                                moves.append((row, column))
                            break
                        else:
                            moves.append((row, column))
                    else:
                        break

            return moves

        def is_legal_move(self, move, board, game):
            moves = self.generate_moves(board, game)
            # Create a temporary board 
            # Check if move takes king out of check or into check
            temp_board = copy.deepcopy(board)
            temp_board = game.make_move([self.position, self.abbr, move], temp_board)
            if self.is_check(temp_board, game):
                return False
            else:
                return move in moves


class Queen(Piece):

        def __init__(self, color, position):
            super().__init__(color, "queen", position, "Q")

        def generate_moves(self, board, game):
            """ Queen's Moves:
            Check position after move is in bounds and is not occupied by anotherpiece
            """
            moves = []

            # Possible standard queen moves
            possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

            # Loop through possible moves until an enemy or boundry is found
            for i, j in possible_moves:
                row, column = self.position
                while True:
                    row += i
                    column += j
                    if 0 <= row < 8 and 0 <= column < 8:
                        if board[(row, column)] is not None:
                            if board[(row, column)].color != self.color:
                                moves.append((row, column))
                            break
                        else:
                            moves.append((row, column))
                    else:
                        break

            return moves

        def is_legal_move(self, move, board, game):
            moves = self.generate_moves(board, game)
            # Create a temporary board 
            # Check if move takes king out of check or into check
            temp_board = copy.deepcopy(board)
            temp_board = game.make_move([self.position, self.abbr, move], temp_board)
            if self.is_check(temp_board, game):
                return False
            else:
                return move in moves


class King(Piece):

        def __init__(self, color, position):
            super().__init__(color, "king", position, "K")

        def generate_moves(self, board, game):
            """King's moves:
            If a move puts the king in check, it is excluded.
            King cannot move out of bounds or into an occupied square.
            King can castle if it hasnt moved, rook has not moved, is not is check, and will not be in check after move
            """

            # Create list of moves
            moves = []
            # List of possible, standard king moves (one in each direction)
            possible_moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

            # Loop through each move
            for i, j in possible_moves:
                row, column = self.position
                row += i
                column += j
                # Check if the move is in bounds and the square is not occupied by ally piece
                if 0 <= row < 8 and 0 <= column < 8 and (board[(row, column)] is None or board[(row, column)].color != self.color):
                    # Temporarily update the board to check if the move puts the king in check
                    temp_board = copy.deepcopy(board)
                    temp_board[self.position] = None
                    temp_board[(row, column)] = self
                    
                    # Check if the king is still under threat after the move
                    danger_squares = []
                    for piece in temp_board.values():
                        if piece is not None and piece.color != self.color and piece.piece_type != 'king':
                            danger_moves = piece.generate_moves(temp_board, game)
                            danger_squares.extend(danger_moves)
                    
                        # If the king is not in check, the move is possible
                    if not (row, column) in danger_squares:
                        moves.append((row, column))
                
                # Check if king can castle
                if self.moves_made == 0:
                    for piece in board.values():
                        if piece is not None:
                            if piece.piece_type == 'rook' and piece.color != self.color:
                                row, col = self.position
                                row1, col1 = piece.position
                                # Rook is on right side
                                if col1 > col:
                                    # Path to rook is empty
                                    if board[row, col + 1] is None and board[row, col + 2] is None:
                                        moves.append((row, col + 2))
                                # rook is on left side:
                                else:  
                                    # Path to rook is empty
                                    if board[row, col - 1] is None and board[row, col - 2] is None and board[row, col - 3] is None:
                                        moves.append((row, col + 2))

            return moves

        def is_legal_move(self, move, board, game):
            # If the move is a castling move, handle it separately
            if self.is_castling_move(move, board):
                return True
            
            moves = self.generate_moves(board, game)
            # Create a temporary board 
            # Check if move takes king out of check or into check
            temp_board = copy.deepcopy(board)
            temp_board = game.make_move([self.position, self.abbr, move], temp_board)
            if self.is_check(temp_board, game):
                return False
            else:
                return move in moves


        def is_castling_move(self, move, board):
            # Check if the move is a castling move
            if abs(move[1] - self.position[1]) == 2 and self.moves_made == 0:
                row, col = self.position
                if self.color == "white" and row == 0:
                    if move[1] > self.position[1]:
                        rook_position = (0, 7)
                    else:
                        rook_position = (0, 0)
                elif self.color == "black" and row == 7:
                    if move[1] > self.position[1]:
                        rook_position = (7, 7)
                    else:
                        rook_position = (7, 0)

                # Check if the rook is in the correct position and has not moved
                rook = board[rook_position]
                if rook is not None and rook.piece_type == "rook" and rook.color == self.color and rook.moves_made == 0:
                    # Check if the squares between the king and the rook are empty
                    if move[1] > self.position[1]:
                        for col in range(self.position[1] + 1, move[1]):
                            if board[(self.position[0], col)] is not None:
                                return False
                    else:
                        for col in range(move[1] + 1, self.position[1]):
                            if board[(self.position[0], col)] is not None:
                                return False

                    return True

            return False



class ChessGame():

        def __init__(self):

            self.board = self.initialize_board()
            self.player1 = "white"
            self.player2 = "black"
            self.turn = "white"
            self.last_move = None
            self.board_states = []
            board_state = self.convert_board_states(self.board)
            self.board_states.append(board_state)
            self.halfmove = 0
            self.fullmove = 1

        @staticmethod
        def initialize_board():
            """
            Define the board as a dictionary
            Place pieces on the board
            """

            board = {}
            for n in range(8):
                for i in range(8):
                    board[(n, i)] = None

            for n in range(8):
                board[(1, n)] = Pawn("white", (1, n))
                board[(6, n)] = Pawn("black", (6, n))

            for n in range(8):
                if n == 0 or n == 7:
                    board[(0, n)] = Rook("white", (0, n))
                    board[(7, n)] = Rook("black", (7, n))
                elif n == 1 or n == 6:
                    board[(0, n)] = Horse("white", (0, n))
                    board[(7, n)] = Horse("black", (7, n))
                elif n == 2 or n == 5:
                    board[(0, n)] = Bishop("white", (0, n))
                    board[(7, n)] = Bishop("black", (7, n))
                elif n == 3:
                    board[(0, n)] = Queen("white", (0, n))
                    board[(7, n)] = Queen("black", (7, n))
                elif n == 4:
                    board[(0, n)] = King("white", (0, n))
                    board[(7, n)] = King("black", (7, n))

            return board


        def get_move(self):
            """
            Get move from players
            """
            player = self.turn
            move_str = input("{}, to move: ".format(player))

            # Check if move in in correct format
            try:
                move_list = move_str.split()
                move = [(int(move_list[0]), int(move_list[1])), move_list[2], (int(move_list[3]), int(move_list[4]))]
                if self.board[move[0]] is not None and self.board[move[0]].abbr == move[1]:
                    if self.board[move[0]].is_legal_move(move[2], self.board, self):
                        return move
            except (SyntaxError, NameError, IndexError):
                pass

            print("Invalid move. Move is in the form 0,1 P 0,2.")
            return self.get_move()

        def make_move(self, move, board):
            row, col = move[0]
            row1, col1 = move[2]

            if board is self.board:
                before_move_count = self.get_piece_count(self.board)

            # Right side castle
            if move[1] == 'K' and col1 - col > 1:
                # Change king's position
                board[move[2]] = board[move[0]]
                board[move[2]].position = move[2]
                board[move[2]].moves_made += 1
                board[move[0]] = None
                # Change rook's position
                if board[(0, 7)] is not None:
                    if self.turn == "white":
                        board[(0, 5)] = board[(0, 7)]
                        board[(0, 5)].position = (0, 5)
                        board[(0, 7)] = None
                if board[(7, 7)] is not None:
                    if self.turn == "black":
                        board[(7, 5)] = board[(7, 7)]
                        board[(7, 5)].position = (7, 5)
                        board[(7, 7)] = None
            # Left side castle
            elif move[1] == 'K' and col - col1 > 1:
                # Change king's position
                board[move[2]] = board[move[0]]
                board[move[2]].position = move[2]
                board[move[2]].moves_made += 1
                board[move[0]] = None
                # Change rook's position
                if board[(0, 0)] is not None:
                    if self.turn == "white":
                        board[(0, 3)] = board[(0, 0)]
                        board[(0, 3)].position = (0, 3)
                        board[(0, 0)] = None
                if board[(7, 0)] is not None:
                    if self.turn == "black":
                        board[(7, 3)] = board[(7, 0)]
                        board[(7, 3)].position = (7, 3)
                        board[(7, 0)] = None

            # If white pawn is on last rank, allow promotion
            elif move[1] == 'P' and row1 == 7:
                board[(6, col)] = None
                board[(7, col1)] = Queen('white', (7, col1))

            # If black pawn in on last rank, allow promotion
            elif move[1] == 'P' and row1 == 0:
                board[(1, col)] = None
                board[(0, col1)] = Queen('black', (0, col1))

            # If move is en passant
            elif move[1] == 'P' and (col1 - col == 1 or col1 - col == -1) and board[move[2]] is None:
                row, col = move[2]
                # Move pawn to new position
                board[move[2]] = board[move[0]]
                board[move[2]].position = move[2]
                board[move[2]].moves_made += 1
                board[move[0]] = None
                # take the pawn using en passant
                if board[move[2]].color == "white":
                    board[(row - 1, col)] = None
                elif board[move[2]].color == "black":
                    board[(row + 1, col)] = None

            # If move is not castling, promotion, or en passant, change position 
            else:
                board[move[2]] = board[move[0]]
                board[move[2]].position = move[2]
                board[move[2]].moves_made += 1
                board[move[0]] = None

            # Change the turn to move, last move, update halfmove clock, and fullmove number
            if board is self.board:
                if self.turn == "black":
                    self.fullmove += 1
                self.turn = "white" if self.turn == "black" else "black"
                self.last_move = move

                after_move_count = self.get_piece_count(self.board)
                if before_move_count == after_move_count:
                    self.halfmove += 1
                elif move[1] != 'P':
                    self.halfmove += 1
                if before_move_count != after_move_count or move[1] == 'P':
                    self.halfmove = 0

            return board


        def is_check(self):

            # Find all squares that are under attack
            is_check = False
            danger_squares = []
            for piece in self.board.values():
                if piece is not None and piece.color != self.turn and piece.piece_type != "king":
                    danger_moves = piece.generate_moves(self.board, self)
                    danger_squares.extend(danger_moves)

            # If king is under attack return True
            for piece in self.board.values():
                if piece is not None:
                    if piece.color == self.turn and piece.piece_type == "king":
                        if piece.position in danger_squares:
                            is_check = True

            return is_check

        def is_checkmate(self):
            is_checkmate = True

            # Must be in check to be in checkmate
            if self.is_check():
                # loop through non-None pieces
                for piece in self.board.values():
                    if piece is not None:
                        # If the piece is the right color, a king, and has no moves, continue
                        if piece.color == self.turn and piece.piece_type == "king":
                            # Create a temporary board and loop through pieces
                            for piece2 in self.board.values():
                                if piece2 is not None:
                                    """ For every piece that is not the king and the correct color,
                                    Generate their moves, make that move in the temporary board
                                    If the move takes the king out of check, it is not checkmate
                                    If no moves take the king out of check, it is checkmate
                                    """
                                    if piece2.color == self.turn:
                                        moves = piece2.generate_moves(self.board, self)
                                        for move in moves:
                                            temp_board = copy.deepcopy(self.board)
                                            temp_board = self.make_move([piece2.position, piece2.abbr, move], temp_board)
                                            for piece in self.board.values():
                                                if piece is not None:
                                                    if piece.color == self.turn and piece.piece_type == "king":
                                                        if not piece.is_check(temp_board, self):
                                                            is_checkmate = False
                                                            break
            else:
                is_checkmate = False

            return is_checkmate


        def is_stalemate(self):
            is_stalemate = False
            num1 = 0
            num2 = 0

            if not self.is_check():
                # loop through every piece of the correct color
                for piece in self.board.values():
                    if piece is not None:
                        if piece.color == self.turn:
                            # Increase num1 for every piece of correct color
                            num1 += 1
                            # Increase num2 if that piece has no legal moves
                            moves = piece.generate_moves(self.board, self)
                            for move in moves:
                                if not piece.is_legal_move(move, self.board, self):
                                    num2 += 1
                            if not moves:
                                num2 += 1
                # If every piece of the correct color has no moves, it is stalemate
                if num1 == num2:
                    is_stalemate = True

            if not is_stalemate:
                board_state = self.convert_board_states(self.board)
                is_stalemate = self.draw_by_rep(board_state)
                
            return is_stalemate


        def draw_by_rep(self, board_state):
            count = 0
            for state in self.board_states:
                if state == board_state:
                    count += 1
                    if count >= 3:
                        return True
            return False
        
        def convert_board_states(self, board):
            board_state = []
            for square in board:
                if board[square] is not None:
                    pos = board[square].position
                    piece_type = board[square].piece_type
                    color = board[square].color
                    board_state.append({pos: (piece_type, color)})
                else:
                    board_state.append(None)

            return board_state


        def map_coordinates_to_chessboard(self, x, y, square_size, top_space, window_width, right_space):
            # Map the coordinates recieved from pygame to squares on board
            row = (y - top_space) // square_size
            col = (x) // square_size

            return row, col

        def play_game(self):
            # Create a method to play in the terminal window
            while True:
                self.print_board()
                if self.is_checkmate():
                    print("Checkmate!")
                    break
                elif self.is_stalemate():
                    print("Stalemate!")
                    break
                move = self.get_move()
                board = self.make_move(move, self.board)
                self.board = board

        
        def get_piece_count(self, board):
            piece_count = 0
            for piece in board.values():
                if piece is not None:
                    piece_count += 1
            
            return piece_count


        def print_board(self, board):
            # Print the board in the terminal
            print(" ", end="")
            for n in range(8):
                print("  ",n, end="")
            print(end='\n')
            print(end='\n')

            vertical = 0
            for n in range(8):
                    for i in range(10):
                        if i == 0:
                            print(' {} '.format(vertical), end="")
                        elif i == 9:
                            print(' {} '.format(vertical))
                            vertical += 1
                        elif board[(n, i - 1)] is None:
                            print(' x  ', end="")
                        else:
                            print(' P  ', end="") if board[(n, i - 1)].piece_type == "pawn" else None
                            print(' B  ', end="") if board[(n, i - 1)].piece_type == "bishop" else None
                            print(' H  ', end="") if board[(n, i - 1)].piece_type == "horse" else None
                            print(' R  ', end="") if board[(n, i - 1)].piece_type == "rook" else None
                            print(' Q  ', end="") if board[(n, i - 1)].piece_type == "queen" else None
                            print(' K  ', end="") if board[(n, i - 1)].piece_type == "king" else None
                    print(end='\n')

            print(" ", end="")
            for n in range(8):
                print("  ",n, end="")
            print(end='\n')
