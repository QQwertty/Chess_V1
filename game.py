import pygame
import chess_game as chess
import ai
import math

# Global Variables
BACKGROUND_COLOR = (32, 32, 32)
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 900
TOP_SPACE = 100
RIGHT_SPACE = 200

# Initialize Pygame
pygame.init()
# Initialize Pygame window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Chess")
screen.fill(BACKGROUND_COLOR)
pygame.display.flip()

# Function to center the piece within the square
def center_piece(row, col, piece_width, piece_height, square_size):
    x_offset = (square_size - piece_width) // 2
    y_offset = (square_size - piece_height) // 2
    return col * square_size + x_offset, row * square_size + y_offset + TOP_SPACE

# Function to draw the chessboard and pieces
def draw_board(board, square_size, game):
    font = pygame.font.Font('freesansbold.ttf', 32)
    if game.is_checkmate():
        text = font.render('Checkmate!', True, (255, 255, 255), pygame.SRCALPHA)
    elif game.is_stalemate():
        text = font.render('Stalemate!', True, (255, 255, 255), pygame.SRCALPHA)
    else:
        text = font.render(game.turn.capitalize() + ' to move', True, (255, 255, 255), pygame.SRCALPHA)
    
    # create a rectangular object for the
    # text surface object
    textRect = text.get_rect()
    
    # set the center of the rectangular object.
    textRect.center = (400, 50)
    for n in range(8):
        if n % 2 == 0:
            alt = 0
        else:
            alt = 1
        for i in range(8):
            if alt == 1:
                pygame.draw.rect(screen, (0, 75, 40), [square_size * i, square_size * n + TOP_SPACE, square_size, square_size], 0)
                alt = 0
            else:
                pygame.draw.rect(screen, (250, 244, 239), [square_size * i, square_size * n + TOP_SPACE, square_size, square_size], 0)
                alt = 1

            if board[(n, i)] is not None:
                piece = board[(n, i)]
                piece_img = pygame.image.load("chesspieces/{}_{}.png".format(piece.color[0], piece.piece_type)).convert_alpha()
                x, y = center_piece(n, i, piece_img.get_width(), piece_img.get_height(), square_size)
                screen.blit(piece_img, (x, y))
    
    # Blit the turn to move to top of screen
    screen.blit(text, textRect)

    # Draw the empty space on the right side (RIGHT_SPACE width)
    pygame.draw.rect(screen, BACKGROUND_COLOR, [WINDOW_WIDTH - RIGHT_SPACE, 0, RIGHT_SPACE, WINDOW_HEIGHT], 0)

    pygame.draw.rect(screen, (255, 255, 255), [WINDOW_WIDTH - RIGHT_SPACE + square_size / 4, 300, 150, 100], 0)
    pygame.draw.rect(screen, (255, 255, 255), [WINDOW_WIDTH - RIGHT_SPACE + square_size / 4, 500, 150, 100], 0)
    pygame.draw.rect(screen, (255, 255, 255), [WINDOW_WIDTH - RIGHT_SPACE + square_size / 4, 700, 150, 100], 0)

    # Update the screen
    pygame.display.update()

game = chess.ChessGame()
square_size = (WINDOW_WIDTH - RIGHT_SPACE) // 8  # Adjust square_size to fit within the available window width

# Draw the initial board
draw_board(game.board, square_size, game)

running = True
piece = None
player = 'white'
ai_color = 'black' if player == 'white' else 'white'
ai = ai.ChessAI(ai_color, game)
mode = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and (game.is_stalemate() or game.is_checkmate()):
            # Add a message to display who won the game or if it was a draw
            if game.is_checkmate():
                print("Checkmate!")
                draw_board(game.board, square_size, game)
            elif game.is_stalemate():
                print("Stalemate!")
                draw_board(game.board, square_size, game)
            x, y = pygame.mouse.get_pos()
            row, col = game.map_coordinates_to_chessboard(x, y, square_size, TOP_SPACE, WINDOW_WIDTH, RIGHT_SPACE)
            if WINDOW_WIDTH - RIGHT_SPACE + square_size / 4 <= x <= WINDOW_WIDTH - RIGHT_SPACE + square_size / 4 + 150:
                if 300 <= y <= 400:
                    game = chess.ChessGame()
                    player = 'black' if player == 'white' else 'white'
                    draw_board(game.board, square_size, game)
                elif 500 <= y <= 600:
                    if mode == 0:
                        mode = 1
                        draw_board(game.board, square_size, game)
                    else:
                        depth = math.floor(.88 ** (game.get_piece_count(game.board) - 16) + 3)
                        move = ai.get_best_move(game.board, ai_color, depth)
                        game.make_move(move, game.board)
                        draw_board(game.board, square_size, game)
                elif 700 <= y <= 800:
                    game = chess.ChessGame()
                    mode = 0
                    draw_board(game.board, square_size, game)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and piece is None:
            x, y = pygame.mouse.get_pos()
            row, col = game.map_coordinates_to_chessboard(x, y, square_size, TOP_SPACE, WINDOW_WIDTH, RIGHT_SPACE)
            if row < 8 and row >= 0 and col < 8 and col >= 0:
                piece = (row, col)
                # print(ai.board_to_FEN(game.board, game.turn))
            elif WINDOW_WIDTH - RIGHT_SPACE + square_size / 4 <= x <= WINDOW_WIDTH - RIGHT_SPACE + square_size / 4 + 150:
                if 300 <= y <= 400:   
                    game = chess.ChessGame()
                    player = 'black' if player == 'white' else 'white'
                    draw_board(game.board, square_size, game)
                elif 500 <= y <= 600:
                    if mode == 0:
                        mode = 1
                        draw_board(game.board, square_size, game)
                    else:
                        depth = math.floor(.88 ** (game.get_piece_count(game.board) - 16) + 3)
                        move = ai.get_best_move(game.board, ai_color, depth)
                        game.make_move(move, game.board)
                        draw_board(game.board, square_size, game)
                elif 700 <= y <= 800:
                    game = chess.ChessGame()
                    mode = 0
                    draw_board(game.board, square_size, game)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and piece is not None:
            x, y = pygame.mouse.get_pos()
            row, col = game.map_coordinates_to_chessboard(x, y, square_size, TOP_SPACE, WINDOW_WIDTH, RIGHT_SPACE)
            if row < 8 and row >= 0 and col < 8 and col >= 0:
                move = (row, col)
                if game.board[piece] is not None:
                    # print([piece, game.board[piece].abbr, move])
                    if player == game.board[piece].color and game.board[piece].is_legal_move(move, game.board, game) and mode == 1:
                        board = game.make_move([piece, game.board[piece].abbr, move], game.board)
                        board_state = game.convert_board_states(board)
                        game.board_states.append(board_state)
                        game.board = board
                        screen.fill(BACKGROUND_COLOR)
                        draw_board(game.board, square_size, game)
                    elif game.turn == game.board[piece].color and game.board[piece].is_legal_move(move, game.board, game) and mode == 0:
                        board = game.make_move([piece, game.board[piece].abbr, move], game.board)
                        board_state = game.convert_board_states(board)
                        game.board_states.append(board_state)
                        game.board = board
                        screen.fill(BACKGROUND_COLOR)
                        draw_board(game.board, square_size, game)
                    piece = None
                else:
                    piece = None



    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Check if the mouse is hovering over the top button
    if WINDOW_WIDTH - RIGHT_SPACE + square_size / 4 <= mouse_x <= WINDOW_WIDTH - RIGHT_SPACE + square_size / 4 + 150 and \
       300 <= mouse_y <= 400:
        pygame.draw.rect(screen, (200, 200, 200), [WINDOW_WIDTH - RIGHT_SPACE + square_size / 4, 300, 150, 100], 0)

    # Check if the mouse is hovering over the middle button
    elif WINDOW_WIDTH - RIGHT_SPACE + square_size / 4 <= mouse_x <= WINDOW_WIDTH - RIGHT_SPACE + square_size / 4 + 150 and \
         500 <= mouse_y <= 600:
        pygame.draw.rect(screen, (200, 200, 200), [WINDOW_WIDTH - RIGHT_SPACE + square_size / 4, 500, 150, 100], 0)

    # Check if the mouse is hovering over the bottom button
    elif WINDOW_WIDTH - RIGHT_SPACE + square_size / 4 <= mouse_x <= WINDOW_WIDTH - RIGHT_SPACE + square_size / 4 + 150 and \
         700 <= mouse_y <= 800:
        pygame.draw.rect(screen, (200, 200, 200), [WINDOW_WIDTH - RIGHT_SPACE + square_size / 4, 700, 150, 100], 0)


    # Draw the buttons
    else:
        pygame.draw.rect(screen, (255, 255, 255), [WINDOW_WIDTH - RIGHT_SPACE + square_size / 4, 300, 150, 100], 0)
        pygame.draw.rect(screen, (255, 255, 255), [WINDOW_WIDTH - RIGHT_SPACE + square_size / 4, 500, 150, 100], 0)
        pygame.draw.rect(screen, (255, 255, 255), [WINDOW_WIDTH - RIGHT_SPACE + square_size / 4, 700, 150, 100], 0)

    # Draw text on the buttons
    font = pygame.font.Font('freesansbold.ttf', 23)
    not_player = 'black' if player == 'white' else 'white'
    text = font.render('Play as ' + not_player, True, (0, 0, 0))
    screen.blit(text, [WINDOW_WIDTH - RIGHT_SPACE + square_size / 4, 330])

    if mode == 0:
        text = font.render('Verse AI', True, (0, 0, 0))
        screen.blit(text, [WINDOW_WIDTH - RIGHT_SPACE + square_size / 2, 530])
    elif mode == 1:
        text = font.render('AI move', True, (0, 0, 0))
        screen.blit(text, [WINDOW_WIDTH - RIGHT_SPACE + square_size / 2, 530])

    text = font.render('Reset', True, (0, 0, 0))
    screen.blit(text, [WINDOW_WIDTH - RIGHT_SPACE + square_size / 2 + 10, 730])

    pygame.display.update()

pygame.quit()
