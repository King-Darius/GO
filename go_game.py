import tkinter as tk
from tkinter import messagebox

BOARD_SIZE = 9
CELL_SIZE = 40
STONE_RADIUS = 16

class GoGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Go Game")
        self.menu_frame = tk.Frame(master)
        self.menu_frame.pack()
        self.board_frame = None
        self.tutorial_frame = None
        self.turn = 'black'
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.captured = {'black': 0, 'white': 0}
        self.show_menu()

    def show_menu(self):
        for widget in self.menu_frame.winfo_children():
            widget.destroy()
        tk.Label(self.menu_frame, text="Welcome to Go!", font=("Arial", 20)).pack(pady=10)
        tk.Button(self.menu_frame, text="Play Game", command=self.start_game, width=20, height=2).pack(pady=5)
        tk.Button(self.menu_frame, text="Tutorial", command=self.show_tutorial, width=20, height=2).pack(pady=5)
        tk.Button(self.menu_frame, text="Exit", command=self.master.quit, width=20, height=2).pack(pady=5)

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
        self.canvas = tk.Canvas(self.board_frame, width=BOARD_SIZE*CELL_SIZE, height=BOARD_SIZE*CELL_SIZE, bg='#f3e2a5')
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.place_stone)
        self.reset_board()
        self.draw_board()
        self.status_label = tk.Label(self.board_frame, text=f"{self.turn.capitalize()}'s turn", font=("Arial", 14))
        self.status_label.pack(pady=5)
        tk.Button(self.board_frame, text="Back to Menu", command=self.back_to_menu, width=15).pack(pady=5)

    def reset_board(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = 'black'
        self.captured = {'black': 0, 'white': 0}

    def draw_board(self):
        self.canvas.delete("all")
        for i in range(BOARD_SIZE):
            self.canvas.create_line(CELL_SIZE//2, CELL_SIZE//2 + i*CELL_SIZE,
                                    CELL_SIZE//2 + (BOARD_SIZE-1)*CELL_SIZE, CELL_SIZE//2 + i*CELL_SIZE)
            self.canvas.create_line(CELL_SIZE//2 + i*CELL_SIZE, CELL_SIZE//2,
                                    CELL_SIZE//2 + i*CELL_SIZE, CELL_SIZE//2 + (BOARD_SIZE-1)*CELL_SIZE)
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                stone = self.board[i][j]
                if stone:
                    x = CELL_SIZE//2 + i*CELL_SIZE
                    y = CELL_SIZE//2 + j*CELL_SIZE
                    color = 'black' if stone == 'black' else 'white'
                    self.canvas.create_oval(
                        x-STONE_RADIUS, y-STONE_RADIUS,
                        x+STONE_RADIUS, y+STONE_RADIUS,
                        fill=color, outline='gray'
                    )

    def place_stone(self, event):
        x = (event.x - CELL_SIZE//2) // CELL_SIZE
        y = (event.y - CELL_SIZE//2) // CELL_SIZE
        if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
            if self.board[x][y] is None:
                self.board[x][y] = self.turn
                self.remove_captured_stones(x, y)
                self.draw_board()
                self.turn = 'white' if self.turn == 'black' else 'black'
                self.status_label.config(text=f"{self.turn.capitalize()}'s turn")
            else:
                messagebox.showinfo("Invalid Move", "This position is already occupied.")

    def remove_captured_stones(self, x, y):
        opponent = 'white' if self.turn == 'black' else 'black'
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                if self.board[nx][ny] == opponent:
                    if not self.has_liberties(nx, ny, opponent, set()):
                        self.capture_group(nx, ny, opponent)

    def has_liberties(self, x, y, color, visited):
        if (x, y) in visited:
            return False
        visited.add((x, y))
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
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
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                if self.board[nx][ny] == color:
                    self.find_group(nx, ny, color, group)

if __name__ == "__main__":
    root = tk.Tk()
    GoGame(root)
    root.mainloop()