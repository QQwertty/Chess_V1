import chess_game
import math
import copy
import os
import csv
import time
import chess
import chess.engine
import numpy as np

engine = chess.engine.SimpleEngine.popen_uci("stockfish-windows-x86-64-avx2.exe")

class ChessAI():
        
        def __init__(self, color, chess_game, max_depth=3):
            self.color = color
            self.max_depth = max_depth
            self.game = chess_game
            self.piece_values = {'P': 100, 'H': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000}
            self.alphabet = 'abcdefgh'



        def evaluate_board(self, board, color, time_limit=.1):
            # Convert the board into FEN notation
            fen_board = self.board_to_FEN(board, color, True)
            
            # Create a chess.Board object from the FEN notation
            eval_board = chess.Board(fen_board)

            # Analyze the board position with Stockfish
            result = engine.analyse(eval_board, chess.engine.Limit(time=time_limit))
            score = result["score"].white().score() if color == "white" else result["score"].black().score()

            return score

        def switch_coordinates(self, piece):
            row, col = piece.position
            row += 7 - 2 * row
            return (row, col)
        

        def get_game_phase(self, board):
            piece_count = 0
            for piece in board.values():
                if piece is not None:
                    piece_count += 1

            if piece_count > 12:
                return 'early'
            return 'late'
        

        def get_best_move(self, board, color, depth):
            tic1 = time.perf_counter()
            self.depth = depth
            folder_path = 'openings'
            files = os.listdir(folder_path)
            fen_board = self.board_to_FEN(board, color)
            
            for file in files:
                with open(os.path.join(folder_path, file)) as f:
                    tsv_reader = csv.DictReader(f, delimiter="\t")
                    for row in tsv_reader:
                        if row['fen'] == fen_board:
                            move_string = row['best_move']
                            move = eval(move_string)
                            return move
            
            move = self.minimax(board, color)
            toc1 = time.perf_counter()
            print(f"1 move minimax time: {toc1 - tic1:0.4f} seconds")

            return move


        def minimax(self, board, color):
            alpha = -math.inf
            beta = math.inf
            scores = []

            for move in self.get_legal_moves(board, color):
                tic = time.perf_counter()
                temp_board = copy.deepcopy(board)
                opp_color = 'white' if color == 'black' else 'black'
                score = self.maxValue(self.game.make_move(move, temp_board), opp_color, 0, alpha, beta)
                dict = {
                    'move': move, 
                    'score': score
                }
                scores.append(dict)

                alpha = max(alpha, score)
                toc = time.perf_counter()
                print(f"1 move minimax time: {toc - tic:0.4f} seconds")

            best_action = max(scores, key=lambda x: x['score'])['move']
            return best_action
            
            
        def minValue(self, board, color, depth, alpha, beta):
            opp_color = 'white' if color == 'black' else 'black'

            if self.game.is_checkmate() or self.game.is_stalemate() or depth == self.max_depth:
                return self.evaluate_board(board, color)

            v = math.inf
            for move in self.get_legal_moves(board, color):
                temp_board = copy.deepcopy(board)
                new_board = self.game.make_move(move, temp_board)
                if new_board is not None:
                    try:
                        v = min(v, self.maxValue(new_board, opp_color, depth + 1, alpha, beta))
                    except:
                        v = v

                    beta = min(beta, v)
                    if beta <= alpha:
                        break

            return v

        def maxValue(self, board, color, depth, alpha, beta):
            opp_color = 'white' if color == 'black' else 'black'

            if self.game.is_checkmate() or self.game.is_stalemate() or depth == self.max_depth:
                return self.evaluate_board(board, color)

            v = -math.inf
            for move in self.get_legal_moves(board, color):
                temp_board = copy.deepcopy(board)
                new_board = self.game.make_move(move, temp_board)
                if new_board is not None:
                    try:
                        v = max(v, self.minValue(new_board, opp_color, depth + 1, alpha, beta))
                    except:
                        v = v

                    alpha = max(alpha, v)
                    if alpha >= beta:
                        break

            return v
            

        def get_legal_moves(self, board, piece_color):
            legal_moves = []
            for piece in board.values():
                if piece is not None:
                    if piece.color == piece_color:
                        moves = piece.generate_moves(board, self.game)
                        for move in moves:
                            if piece.is_legal_move(move, board, self.game):
                                legal_moves.append([piece.position, piece.abbr, move])

            return legal_moves
        

        def flip_board(self, board):
            flip_board = copy.deepcopy(board)
            for piece in flip_board:
                flip_board[piece] = None

            for piece in board.values():
                if piece is not None:
                    pos = self.switch_coordinates(piece)
                    flip_board[pos] = piece
            return flip_board
        

        def board_to_FEN(self, board, turn, with_moves=False):
            # Convert the board into Forsyth–Edwards Notation
            game = self.game
            flip_board = self.flip_board(board)
            fen_board = []
            for count, piece in enumerate(flip_board.values(), 1):
                if piece is not None:
                    if piece.color == 'white':
                        if piece.abbr == 'H':
                            fen_board.append('N')
                        else:
                            fen_board.append(piece.abbr)
                    elif piece.color == 'black':
                        if piece.abbr == 'H':
                            fen_board.append('n')
                        else:
                            fen_board.append(piece.abbr.lower())
                else:
                    try:
                        fen_board[-1] += 1
                    except:
                        fen_board.append(1)
                if count % 8 == 0 and count != 64:
                    fen_board.append('/')
            
            fen_board.append(' {} '.format(turn[0].lower()))
            fen_board.append(self.can_castle(board))
            if with_moves == True:
                if game.last_move != None:
                    if game.last_move[1] == 'P':
                        r_pos, c_pos = game.last_move[0]
                        r_move, c_move = game.last_move[2]
                        if r_move - r_pos == 2:
                            move = self.alphabet[c_move] + '{}'.format(r_move)
                            fen_board.append(' {} '.format(move))
                        elif r_move - r_pos == -2:
                            move = self.alphabet[c_move] + '{}'.format(r_move + 2)
                            fen_board.append(' {} '.format(move))
                        else:
                            fen_board.append(' - ')
                    else:
                        fen_board.append(' - ')
                else:
                    fen_board.append(' - ')
            
                fen_board.append('{} '.format(game.halfmove))
                fen_board.append('{}'.format(game.fullmove))

            fen_board_str = ''
            for ele in fen_board:
                fen_board_str += str(ele)

            return fen_board_str
        

        def can_castle(self, board):
            # Return if the kings can castle in FEN notation
            # ex: KQkq ; "K" if White can castle kingside, "Q" if White can castle queenside, "k" if Black can castle kingside, and "q" if Black can castle queenside.
            fen_not = ''
            for king in board.values():
                if king is not None:
                    if king.piece_type == "king" and king.moves_made == 0:
                        if king.color == 'white':
                            for rook in board.values():
                                if rook is not None:
                                    if rook.piece_type == 'rook' and rook.color == king.color and rook.moves_made == 0:
                                        if rook.position == (0, 0):
                                            fen_not = fen_not + 'Q'
                                        else:
                                            fen_not = 'K' + fen_not

                        elif king.color == 'black':
                            for rook in board.values():
                                if rook is not None:
                                    if rook.piece_type == 'rook' and rook.color == king.color and rook.moves_made == 0:
                                        if rook.position == (7, 0):
                                            fen_not = fen_not + 'q'
                                        else:
                                            try:
                                                fen_not = fen_not[0] + fen_not[1] + 'k' + fen_not[2]
                                            except:
                                                fen_not = 'kq'
            if fen_not == '':
                fen_not = '-'
            return fen_not
                                