import tkinter as tk
from tkinter import messagebox, Toplevel
import time

# Author : Seungchan LEE

# SUM and SUB Gomoku
# Rules
# 1) Each Player initially has 20 Stones, (1,2,3,4,5) * 4sets
# 2) Black Player makes first move
# 3) @ First move, Black player can only place stones which less than 3
# 4) After each moves, (sum of my stones of consecutive row - sum of opponent stones of same row) reaches 16(not above 16), player wins.
# 5) (4) Applies all consecutive rows(contains column, diagonals).
# 6) No forbidden move except (3).

# How to use this program
# 1) Run Python script.
# 2) Click intersection point to make move.
# 3) After click, Number selection will appear.
# 4) If some player wins, program will be get into halt, and highlight last movement.

# Constants
BOARD_SIZE = 15
CELL_SIZE = 40
BLACK, WHITE, EMPTY = 1, 2, 0

class OmokGame:
    def __init__(self, root):
        self.root = root
        self.root.title("합차 오목")
        self.canvas = tk.Canvas(self.root, width=BOARD_SIZE * CELL_SIZE, height=BOARD_SIZE * CELL_SIZE, bg="lightyellow")
        self.canvas.pack()
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.black_stones = [1, 2, 3, 4, 5] * 4  # Player 1 stones
        self.white_stones = [1, 2, 3, 4, 5] * 4  # Player 2 stones
        self.current_player = BLACK
        self.last_move = None
        self.turn_count = 0
        self.canvas.bind("<Button-1>", self.handle_click)
        self.draw_board()

    def draw_board(self):
        for i in range(BOARD_SIZE):
            self.canvas.create_line(i * CELL_SIZE + CELL_SIZE // 2, CELL_SIZE // 2,
                                     i * CELL_SIZE + CELL_SIZE // 2, BOARD_SIZE * CELL_SIZE - CELL_SIZE // 2, fill="black")
            self.canvas.create_line(CELL_SIZE // 2, i * CELL_SIZE + CELL_SIZE // 2,
                                     BOARD_SIZE * CELL_SIZE - CELL_SIZE // 2, i * CELL_SIZE + CELL_SIZE // 2, fill="black")

    def handle_click(self, event):
        # Get grid position
        x = round((event.x - CELL_SIZE // 2) / CELL_SIZE)
        y = round((event.y - CELL_SIZE // 2) / CELL_SIZE)

        if x < 0 or x >= BOARD_SIZE or y < 0 or y >= BOARD_SIZE:
            return
        if self.board[y][x] != EMPTY:
            return

        # Select stone value via GUI
        available_stones = self.black_stones if self.current_player == BLACK else self.white_stones
        if self.turn_count == 0 and self.current_player == BLACK:
            valid_choices = sorted([v for v in available_stones if v in [1, 2, 3]])
        else:
            valid_choices = sorted(available_stones)

        stone_value = self.prompt_stone_value(valid_choices)
        if stone_value is None:
            return  # Cancel or invalid input

        available_stones.remove(stone_value)
        self.board[y][x] = (self.current_player, stone_value)
        self.draw_stone(x, y, self.current_player, stone_value)
        self.last_move = (x, y)  # Save the last move

        # Check the entire board for winning condition
        if self.check_winner_after_move():
            return

        self.current_player = WHITE if self.current_player == BLACK else BLACK
        self.turn_count += 1

    def prompt_stone_value(self, valid_choices):
        popup = Toplevel(self.root)
        popup.title("Choose a Stone")
        popup.geometry("500x200")
        popup.resizable(True, True)  # Allow resizing of the popup

        result = [None]  # Mutable object to capture the result

        def choose_value(value):
            result[0] = value
            popup.destroy()

        max_columns = 8  # Maximum number of stones per row
        for idx, value in enumerate(valid_choices):
            row = idx // max_columns
            col = idx % max_columns
            color = "black" if self.current_player == BLACK else "white"
            btn = tk.Canvas(popup, width=40, height=40, bg="lightyellow", highlightthickness=1, highlightbackground="black")
            btn.grid(row=row, column=col, padx=5, pady=5)
            btn.create_oval(5, 5, 35, 35, fill=color)
            btn.create_text(20, 20, text=str(value), fill="yellow" if self.current_player == BLACK else "blue")
            btn.bind("<Button-1>", lambda e, v=value: choose_value(v))

        popup.wait_window()
        return result[0]

    def draw_stone(self, x, y, player, value):
        color = "black" if player == BLACK else "white"
        cx = x * CELL_SIZE + CELL_SIZE // 2
        cy = y * CELL_SIZE + CELL_SIZE // 2
        self.canvas.create_oval(
            cx - 15, cy - 15,
            cx + 15, cy + 15,
            fill=color
        )
        self.canvas.create_text(cx, cy, text=str(value), fill="yellow" if player == BLACK else "blue")

    def get_stone_group_in_direction(self, x, y, dx, dy):
        """
        Get all stones in a single connected group in the given direction (dx, dy).
        """
        group = [(x, y)]  # Start with the current position

        # Move in the positive direction
        nx, ny = x + dx, y + dy
        while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
            if self.board[ny][nx] == EMPTY:
                break
            group.append((nx, ny))
            nx += dx
            ny += dy

        # Move in the negative direction
        nx, ny = x - dx, y - dy
        while 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
            if self.board[ny][nx] == EMPTY:
                break
            group.append((nx, ny))
            nx -= dx
            ny -= dy

        return group

    def calculate_score_for_group(self, group, player):
        """
        Calculate the score for a given group of stones.
        """
        total_score = 0
        opponent = WHITE if player == BLACK else BLACK

        for (x, y) in group:
            if self.board[y][x][0] == player:
                total_score += self.board[y][x][1]  # Add value of player's stone
            elif self.board[y][x][0] == opponent:
                total_score -= self.board[y][x][1]  # Subtract value of opponent's stone

        return total_score

    def calculate_board_scores(self):
        """
        Calculate the maximum score for Black and White by checking all possible groups on the board.
        """
        max_black_score = 0
        max_white_score = 0

        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                if self.board[y][x] == EMPTY:
                    continue
                player = self.board[y][x][0]

                # Check all directions from this stone
                directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
                for dx, dy in directions:
                    group = self.get_stone_group_in_direction(x, y, dx, dy)
                    score = self.calculate_score_for_group(group, player)

                    # Update maximum scores
                    if player == BLACK:
                        max_black_score = max(max_black_score, score)
                    elif player == WHITE:
                        max_white_score = max(max_white_score, score)

        # Print maximum scores for debugging
        print(f"Max Black Score: {max_black_score}")
        print(f"Max White Score: {max_white_score}")

        return max_black_score, max_white_score

    def check_winner_after_move(self):
        """
        Check the entire board for the winning condition after every move.
        """
        max_black_score, max_white_score = self.calculate_board_scores()

        # Check if either player has a winning score
        if max_black_score == 16:
            print("Black wins with a score of", max_black_score)
            if self.last_move:
                self.highlight_winning_stone(*self.last_move)  # Highlight the winning stone
            self.canvas.update()
            time.sleep(2)  # Wait for 2 seconds before resetting
            messagebox.showinfo("Game Over", "Black wins!")
            self.reset_game()
            return True
        elif max_white_score == 16:
            print("White wins with a score of", max_white_score)
            if self.last_move:
                self.highlight_winning_stone(*self.last_move)  # Highlight the winning stone
            self.canvas.update()
            time.sleep(2)  # Wait for 2 seconds before resetting
            messagebox.showinfo("Game Over", "White wins!")
            self.reset_game()
            return True

        return False

    def highlight_winning_stone(self, x, y):
        """
        Highlight the winning stone on the board.
        """
        cx = x * CELL_SIZE + CELL_SIZE // 2
        cy = y * CELL_SIZE + CELL_SIZE // 2
        self.canvas.create_oval(
            cx - 20, cy - 20,
            cx + 20, cy + 20,
            outline="red", width=4
        )

    def reset_game(self):
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.black_stones = [1, 2, 3, 4, 5] * 4
        self.white_stones = [1, 2, 3, 4, 5] * 4
        self.current_player = BLACK
        self.turn_count = 0
        self.last_move = None
        self.canvas.delete("all")
        self.draw_board()

if __name__ == "__main__":
    root = tk.Tk()
    game = OmokGame(root)
    root.mainloop()
