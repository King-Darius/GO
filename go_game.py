import json
import os
import random
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext

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
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.menu_frame = tk.Frame(master)
        self.menu_frame.pack()
        self.board_frame = None
        self.tutorial_frame = None
        self.guide_frame = None
        self.turn = PLAYER_BLACK
        self.board_size = DEFAULT_BOARD_SIZE
        self.board = []
        self.captured = {PLAYER_BLACK: 0, PLAYER_WHITE: 0}
        self.last_move = None
        self.ai_enabled = False
        self.gtp_engine = None
        self.ai_thinking = False
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

        tk.Button(self.menu_frame, text="Quick Tutorial", command=self.show_tutorial, width=20, height=2).pack(pady=5)
        tk.Button(self.menu_frame, text="Complete Go Guide", command=self.show_guide, width=20, height=2).pack(pady=5)
        tk.Button(self.menu_frame, text="Exit", command=self.on_close, width=20, height=2).pack(pady=5)

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
            "This quick tutorial covers the essentials so you can start playing immediately.\n\n"
            "1. Opening Move\n"
            "   Black plays first. Use the intersections of the lines, not the squares.\n\n"
            "2. Liberties\n"
            "   Stones need at least one adjacent empty point (up, down, left, or right).\n\n"
            "3. Captures\n"
            "   If every liberty of a stone or connected group is filled by the opponent, it is captured.\n\n"
            "4. Illegal Self-Capture\n"
            "   You cannot play a move that would leave your own stone without liberties unless it captures.\n\n"
            "5. Ending the Game\n"
            "   When both players pass in a row, count territory plus captured stones.\n\n"
            "Tip: Build strong groups with eyes (internal liberties) so they cannot be captured easily."
        )
        tk.Label(self.tutorial_frame, text=tutorial_text, justify=tk.LEFT, font=("Arial", 13), wraplength=720).pack(padx=20, pady=20)
        tk.Button(self.tutorial_frame, text="Back to Menu", command=self.back_to_menu, width=15).pack(pady=10)

    def show_guide(self):
        self.menu_frame.pack_forget()
        self.guide_frame = tk.Frame(self.master)
        self.guide_frame.pack(fill=tk.BOTH, expand=True)
        guide_text = (
            "GO MASTERCLASS GUIDE\n"
            "===================\n\n"
            "1. Equipment & Setup\n"
            "   • 19x19 is the traditional board, while 9x9 or 13x13 help you learn faster.\n"
            "   • Black takes the first move; stones are placed on intersections.\n\n"
            "2. Liberties & Captures\n"
            "   • Liberties are the empty points directly next to a stone (not diagonals).\n"
            "   • Connected stones share liberties; a group is captured when it loses them all.\n\n"
            "3. Life & Death\n"
            "   • Living groups secure two separate \"eyes\"—internal empty points no enemy can fill.\n"
            "   • Reading out life-and-death fights improves with practice on smaller boards.\n\n"
            "4. Ko Rule\n"
            "   • Repeating a previous board position is forbidden.\n"
            "   • After a ko capture, play elsewhere before re-capturing the same point.\n\n"
            "5. Territories & Scoring\n"
            "   • Your score: surrounded empty points + stones you captured.\n"
            "   • White receives komi (bonus points, typically 6.5–7.5) to offset Black's first move.\n\n"
            "6. Strategic Themes\n"
            "   • Fuseki: Balance building frameworks with reducing the opponent's potential.\n"
            "   • Joseki: Study common corner sequences to get fair local results.\n"
            "   • Sente vs. Gote: Moves that demand a reply give you initiative to steer the game.\n"
            "   • Influence vs. Territory: Decide whether to build outward strength or solidify points.\n"
            "   • Yose: In the endgame, count carefully—half-point swings are common!\n\n"
            "7. Flow of Play\n"
            "   • Players alternate moves until both pass consecutively.\n"
            "   • Remove clearly dead groups by agreement before tallying territory.\n\n"
            "8. Study Plan\n"
            "   • Review games with stronger players or AI (like KataGo) to find better moves.\n"
            "   • Practice tsumego (life-and-death problems) daily to sharpen reading.\n"
            "   • Explore professional games to learn shape, timing, and whole-board thinking.\n\n"
            "Have fun exploring Go's depth! Use the strong AI opponent to experiment with new ideas."
        )
        text_widget = scrolledtext.ScrolledText(self.guide_frame, wrap=tk.WORD, font=("Arial", 12))
        text_widget.insert(tk.END, guide_text)
        text_widget.configure(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        tk.Button(self.guide_frame, text="Back to Menu", command=self.back_to_menu, width=15).pack(pady=10)

    def back_to_menu(self):
        self._close_engine()
        if self.tutorial_frame:
            self.tutorial_frame.pack_forget()
            self.tutorial_frame = None
        if self.guide_frame:
            self.guide_frame.pack_forget()
            self.guide_frame = None
        if self.board_frame:
            self.board_frame.pack_forget()
        self.menu_frame.pack()

    def on_close(self):
        self._close_engine()
        self.master.destroy()

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
        self.capture_label = tk.Label(
            self.board_frame,
            text=self._capture_text(),
            font=("Arial", 12)
        )
        self.capture_label.pack(pady=2)
        tk.Button(self.board_frame, text="Back to Menu", command=self.back_to_menu, width=15).pack(pady=5)
        if self.ai_enabled:
            self._start_engine()
            if self.turn == PLAYER_WHITE:
                self.master.after(500, self.ai_move)

    def reset_board(self):
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.turn = PLAYER_BLACK
        self.captured = {PLAYER_BLACK: 0, PLAYER_WHITE: 0}
        self.last_move = None
        self.ai_thinking = False

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
        if self.ai_thinking:
            return
        if 0 <= i < self.board_size and 0 <= j < self.board_size:
            if self.board[i][j] is None:
                self.board[i][j] = self.turn
                self.last_move = (i, j)
                self.remove_captured_stones(i, j)
                self.draw_board()
                self._update_engine_with_move(self.turn, (i, j))
                self.switch_turn()
            else:
                messagebox.showinfo("Invalid Move", "This position is already occupied.")

    def switch_turn(self):
        self.turn = PLAYER_WHITE if self.turn == PLAYER_BLACK else PLAYER_BLACK
        self.status_label.config(text=f"{self.turn.capitalize()}'s turn")
        if hasattr(self, 'capture_label'):
            self.capture_label.config(text=self._capture_text())
        if self.ai_enabled and self.turn == PLAYER_WHITE:
            self.master.after(500, self.ai_move)

    def ai_move(self):
        if self.gtp_engine:
            self.ai_thinking = True
            threading.Thread(target=self._engine_move_thread, daemon=True).start()
        else:
            self._fallback_ai_move()

    def _engine_move_thread(self):
        try:
            move = self.gtp_engine.genmove(self.turn)
        except Exception as exc:
            self.master.after(0, lambda: self._handle_engine_failure(exc))
            return
        self.master.after(0, lambda: self._apply_ai_move(move))

    def _apply_ai_move(self, move):
        self.ai_thinking = False
        if move is None:
            messagebox.showinfo("Game Over", "AI passes. No further moves available.")
            return
        i, j = move
        if self.board[i][j] is None:
            self.board[i][j] = self.turn
            self.last_move = (i, j)
            self.remove_captured_stones(i, j)
            self.draw_board()
            self.switch_turn()
        else:
            messagebox.showwarning("AI Error", "AI attempted an invalid move. Switching to fallback AI.")
            self._close_engine()
            self._fallback_ai_move()

    def _fallback_ai_move(self):
        move = self._choose_ai_move(self.turn)
        if move is None:
            messagebox.showinfo("Game Over", "No moves available for AI.")
            return
        i, j = move
        self.board[i][j] = self.turn
        self.last_move = (i, j)
        self.remove_captured_stones(i, j)
        self.draw_board()
        self.switch_turn()

    def _choose_ai_move(self, color):
        legal_moves = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] is not None:
                    continue
                simulation = self._simulate_move(color, (i, j))
                if simulation is None:
                    continue
                legal_moves.append(((i, j), simulation))
        if not legal_moves:
            return None

        best_score = float("-inf")
        best_moves = []
        for (move, simulation) in legal_moves:
            board_after, captured, liberties = simulation
            score = self._score_move(color, move, board_after, captured, liberties)
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        return random.choice(best_moves)

    def _simulate_move(self, color, move):
        i, j = move
        if self.board[i][j] is not None:
            return None
        board_copy = [column[:] for column in self.board]
        board_copy[i][j] = color
        opponent = PLAYER_WHITE if color == PLAYER_BLACK else PLAYER_BLACK
        captured = 0

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = i + dx, j + dy
            if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                if board_copy[nx][ny] == opponent:
                    group, liberties = self._collect_group(board_copy, nx, ny)
                    if not liberties:
                        for gx, gy in group:
                            board_copy[gx][gy] = None
                            captured += 1

        group, liberties = self._collect_group(board_copy, i, j)
        if not liberties and captured == 0:
            return None
        return board_copy, captured, len(liberties)

    def _score_move(self, color, move, board_after, captured, liberties):
        opponent = PLAYER_WHITE if color == PLAYER_BLACK else PLAYER_BLACK
        i, j = move
        score = 0.0

        score += captured * 60
        score += liberties * 6

        friendly_adjacent = 0
        opponent_adjacent = 0
        defensive_bonus = 0
        offensive_bonus = 0

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = i + dx, j + dy
            if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                occupant_before = self.board[nx][ny]
                if occupant_before == color:
                    friendly_adjacent += 1
                    group, libs = self._collect_group(self.board, nx, ny)
                    if len(libs) == 1:
                        defensive_bonus += 45
                    elif len(libs) == 2:
                        defensive_bonus += 15
                elif occupant_before == opponent:
                    opponent_adjacent += 1

                occupant_after = board_after[nx][ny]
                if occupant_after == opponent:
                    group_after, libs_after = self._collect_group(board_after, nx, ny)
                    if len(libs_after) == 1:
                        offensive_bonus += 35

        score += friendly_adjacent * 5
        score += opponent_adjacent * 3
        score += defensive_bonus
        score += offensive_bonus

        if liberties == 1 and captured == 0:
            score -= 55

        distance_penalty = self._distance_to_center(move) * 4
        score -= distance_penalty

        if i == 0 or j == 0 or i == self.board_size - 1 or j == self.board_size - 1:
            score -= 3

        score += random.uniform(0, 1)
        return score

    def _collect_group(self, board_state, x, y):
        color = board_state[x][y]
        if color is None:
            return set(), set()
        group = set()
        liberties = set()
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in group:
                continue
            group.add((cx, cy))
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                    occupant = board_state[nx][ny]
                    if occupant is None:
                        liberties.add((nx, ny))
                    elif occupant == color and (nx, ny) not in group:
                        stack.append((nx, ny))
        return group, liberties

    def _distance_to_center(self, move):
        cx = (self.board_size - 1) / 2
        cy = (self.board_size - 1) / 2
        i, j = move
        return ((i - cx) ** 2 + (j - cy) ** 2) ** 0.5

    def _start_engine(self):
        config_path = os.path.join(os.path.dirname(__file__), "engine_config.json")
        if not os.path.exists(config_path):
            return
        self._close_engine()
        try:
            with open(config_path, "r", encoding="utf-8") as cfg:
                data = json.load(cfg)
            command = data.get("command")
            if not command:
                raise ValueError("Engine command missing in configuration file.")
            startup_commands = data.get("startup_commands", [])
            self.gtp_engine = GtpEngine(command, self.board_size, startup_commands)
        except Exception as exc:
            messagebox.showwarning("Engine Error", f"Failed to start external AI engine.\nUsing fallback AI instead.\n{exc}")
            self.gtp_engine = None

    def _update_engine_with_move(self, color, coords):
        if self.gtp_engine:
            try:
                self.gtp_engine.play(color, coords)
            except Exception as exc:
                messagebox.showwarning("Engine Error", f"Engine stopped responding. Switching to fallback AI.\n{exc}")
                self._close_engine()

    def _handle_engine_failure(self, exc):
        self.ai_thinking = False
        messagebox.showwarning("Engine Error", f"Engine move failed. Switching to fallback AI.\n{exc}")
        self._close_engine()
        self._fallback_ai_move()

    def _close_engine(self):
        if self.gtp_engine:
            try:
                self.gtp_engine.close()
            except Exception:
                pass
            self.gtp_engine = None

    def _capture_text(self):
        return (
            f"Captured stones - Black: {self.captured[PLAYER_WHITE]}  "
            f"White: {self.captured[PLAYER_BLACK]}"
        )

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
            opponent = PLAYER_WHITE if color == PLAYER_BLACK else PLAYER_BLACK
            self.captured[opponent] += 1

    def find_group(self, x, y, color, group):
        if (x, y) in group:
            return
        group.add((x, y))
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                if self.board[nx][ny] == color:
                    self.find_group(nx, ny, color, group)


class GtpEngine:
    def __init__(self, command, board_size, startup_commands=None):
        if isinstance(command, str):
            command = command.split()
        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        self.board_size = board_size
        self._send(f"boardsize {board_size}")
        self._send("clear_board")
        self._send("komi 7.5")
        for extra in startup_commands or []:
            self._send(extra)

    def _read_response(self):
        lines = []
        while True:
            line = self.process.stdout.readline()
            if line == "":
                raise RuntimeError("Engine process terminated unexpectedly.")
            line = line.rstrip("\n")
            if line == "":
                break
            lines.append(line)
        if not lines:
            return ""
        status = lines[0]
        if status.startswith("?"):
            raise RuntimeError("Engine error: " + "\n".join(lines))
        if status.startswith("="):
            return status[1:].strip()
        return lines[-1]

    def _send(self, command):
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()
        return self._read_response()

    def play(self, color, coords):
        move = coords_to_gtp(coords, self.board_size)
        self._send(f"play {color} {move}")

    def genmove(self, color):
        result = self._send(f"genmove {color}")
        if result.lower() == "pass":
            return None
        return gtp_to_coords(result, self.board_size)

    def close(self):
        try:
            self._send("quit")
        finally:
            self.process.terminate()


def coords_to_gtp(coords, board_size):
    i, j = coords
    column_letters = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
    if i >= len(column_letters):
        raise ValueError("Board size too large for coordinate conversion.")
    letter = column_letters[i]
    number = board_size - j
    return f"{letter}{number}"


def gtp_to_coords(gtp_str, board_size):
    gtp_str = gtp_str.strip().upper()
    column_letters = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
    letter = gtp_str[0]
    if letter not in column_letters:
        raise ValueError(f"Invalid GTP move: {gtp_str}")
    i = column_letters.index(letter)
    number = int(gtp_str[1:])
    if number < 1 or number > board_size:
        raise ValueError(f"GTP move out of range: {gtp_str}")
    j = board_size - number
    return i, j


if __name__ == "__main__":
    root = tk.Tk()
    GoGame(root)
    root.mainloop()
