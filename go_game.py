import tkinter as tk
from tkinter import messagebox

DEFAULT_BOARD_SIZE = 9
CELL_SIZE = 40
STONE_RADIUS = 16
PLAYER_BLACK = 'black'
PLAYER_WHITE = 'white'

BOARD_SIZES = [9, 13, 19]

class GoGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Go Game")
        self.menu_frame = tk.Frame(master)
        self.menu_frame.pack()
        self.board_frame = None
        self.tutorial_frame = None
        self.turn = PLAYER_BLACK
        self.board_size = DEFAULT_BOARD_SIZE
        self.board = []
        self.captured = {PLAYER_BLACK: 0, PLAYER_WHITE: 0}
        self.last_move = None
        self.ai_enabled = False
        self.show_menu()

    def show_menu(self):
        for widget in self.menu_frame.winfo_children():
            widget.destroy()
        tk.Label(self.menu_frame, text="Welcome to Go!", font=("Arial", 20)).pack(pady=10)
        tk.Label(self.menu_frame, text="Select Board Size:", font=("Arial", 14)).pack(pady=5)

        for size in BOARD_SIZES:
            tk.Button(
                self.menu_frame, text=f"{size} x {size} Human vs Human",
                command=lambda s=size: self.select_board_size(s, False),
                width=20, height=2
            ).pack(pady=2)
            tk.Button(
                self.menu_frame, text=f"{size} x {size} Human vs AI",
                command=lambda s=size: self.select_board_size(s, True),
                width=20, height=2
            ).pack(pady=2)

        tk.Button(self.menu_frame, text="Tutorial", command=self.show_tutorial, width=20, height=2).pack(pady=5)
        tk.Button(self.menu_frame, text="Exit", command=self.master.quit, width=20, height=2).pack(pady=5)

    def select_board_size(self, size, ai_enabled):
        self.board_size = size
        self.ai_enabled = ai_enabled
        self.start_game()

    def show_tutorial(self):
        self.menu_frame.pack_forget()
        self.tutorial_frame = tk.Frame(self.master)
        self.tutorial_frame.pack(fill=tk.BOTH, expand=True)
        tutorial_text = (
            "Welcome to Go!\n\n"
            "Go is a strategy board game for two players.\n"
            "Players take turns placing stones (black or white) on the intersections of the board.\n"
            "The goal is to control the most territory on the board.\n"
            "Stones are captured when they are surrounded on all orthogonal sides.\n"
            "The game ends when both players pass, and territory is counted.\n\n"
            "How to Play:\n"
            "- Click on empty intersections to place your stone.\n"
            "- Try to surround your opponent's stones or spaces.\n"
            "- You cannot place a stone where it would be immediately captured.\n"
            "- Press 'Back to Menu' at any time to return.\n\n"
            "Ready to play? Click 'Back to Menu' and start your first game!"
        )
        tk.Label(self.tutorial_frame, text=tutorial_text, justify=tk.LEFT, font=("Arial", 14)).pack(padx=20, pady=20)
        tk.Button(self.tutorial_frame, text="Back to Menu", command=self.back_to_menu, width=15).pack(pady=10)

    def back_to_menu(self):
        if self.tutorial_frame:
            self.tutorial_frame.pack_forget()
        if self.board_frame:
            self.board_frame.pack_forget()
        self.menu_frame.pack()

    def start_game(self):
        self.menu_frame.pack_forget()
        self.board_frame = tk.Frame(self.master)
        self.board_frame.pack()
        self.canvas = tk.Canvas(
            self.board_frame,
            width=self.board_size * CELL_SIZE,
            height=self.board_size * CELL_SIZE,
            bg='#f3e2a5'
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.place_stone)
        self.reset_board()
        self.draw_board()
        self.status_label = tk.Label(self.board_frame, text=f"{self.turn.capitalize()}'s turn", font=("Arial", 14))
        self.status_label.pack(pady=5)
        tk.Button(self.board_frame, text="Back to Menu", command=self.back_to_menu, width=15).pack(pady=5)
        if self.ai_enabled and self.turn == PLAYER_WHITE:
            self.master.after(500, self.ai_move)
        elif self.ai_enabled and self.turn == PLAYER_BLACK:
            pass

    def reset_board(self):
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.turn = PLAYER_BLACK
        self.captured = {PLAYER_BLACK: 0, PLAYER_WHITE: 0}
        self.last_move = None

    def draw_board(self):
        self.canvas.delete("all")
        for i in range(self.board_size):
            self.canvas.create_line(CELL_SIZE//2, CELL_SIZE//2 + i*CELL_SIZE,
                                    CELL_SIZE//2 + (self.board_size-1)*CELL_SIZE, CELL_SIZE//2 + i*CELL_SIZE)
            self.canvas.create_line(CELL_SIZE//2 + i*CELL_SIZE, CELL_SIZE//2,
                                    CELL_SIZE//2 + i*CELL_SIZE, CELL_SIZE//2 + (self.board_size-1)*CELL_SIZE)
        for i in range(self.board_size):
            for j in range(self.board_size):
                stone = self.board[i][j]
                x = CELL_SIZE//2 + i*CELL_SIZE
                y = CELL_SIZE//2 + j*CELL_SIZE
                if stone:
                    color = 'black' if stone == PLAYER_BLACK else 'white'
                    self.canvas.create_oval(
                        x-STONE_RADIUS, y-STONE_RADIUS,
                        x+STONE_RADIUS, y+STONE_RADIUS,
                        fill=color, outline='gray'
                    )
                if self.last_move == (i, j):
                    self.canvas.create_rectangle(
                        x-STONE_RADIUS-2, y-STONE_RADIUS-2,
                        x+STONE_RADIUS+2, y+STONE_RADIUS+2,
                        outline='red', width=2
                    )

    def place_stone(self, event):
        x_pixel, y_pixel = event.x, event.y
        i = int(round((x_pixel - CELL_SIZE//2) / CELL_SIZE))
        j = int(round((y_pixel - CELL_SIZE//2) / CELL_SIZE))
        if 0 <= i < self.board_size and 0 <= j < self.board_size:
            if self.board[i][j] is None:
                self.board[i][j] = self.turn
                self.last_move = (i, j)
                self.remove_captured_stones(i, j)
                self.draw_board()
                self.switch_turn()
            else:
                messagebox.showinfo("Invalid Move", "This position is already occupied.")

    def switch_turn(self):
        self.turn = PLAYER_WHITE if self.turn == PLAYER_BLACK else PLAYER_BLACK
        self.status_label.config(text=f"{self.turn.capitalize()}'s turn")
        if self.ai_enabled and self.turn == PLAYER_WHITE:
            self.master.after(500, self.ai_move)

    def ai_move(self):
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] is None:
                    self.board[i][j] = self.turn
                    self.last_move = (i, j)
                    self.remove_captured_stones(i, j)
                    self.draw_board()
                    self.switch_turn()
                    return
        messagebox.showinfo("Game Over", "No moves available for AI.")

    def remove_captured_stones(self, x, y):
        opponent = PLAYER_WHITE if self.turn == PLAYER_BLACK else PLAYER_BLACK
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                if self.board[nx][ny] == opponent:
                    if not self.has_liberties(nx, ny, opponent, set()):
                        self.capture_group(nx, ny, opponent)

    def has_liberties(self, x, y, color, visited):
        if (x, y) in visited:
            return False
        visited.add((x, y))
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                if self.board[nx][ny] is None:
                    return True
                if self.board[nx][ny] == color:
                    if self.has_liberties(nx, ny, color, visited):
                        return True
        return False

    def capture_group(self, x, y, color):
        to_remove = set()
        self.find_group(x, y, color, to_remove)
        for rx, ry in to_remove:
            self.board[rx][ry] = None
            self.captured[color] += 1

    def find_group(self, x, y, color, group):
        if (x, y) in group:
            return
        group.add((x, y))
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                if self.board[nx][ny] == color:
                    self.find_group(nx, ny, color, group)

if __name__ == "__main__":
    root = tk.Tk()
    GoGame(root)
    root.mainloop()