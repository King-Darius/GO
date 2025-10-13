# Go Game (Weiqi/Baduk) - Easy Desktop App

This is a simple Go game for beginners, runnable by anyone (no coding required).

## Features

- Play on 9x9, 13x13, or full-size 19x19 boards.
- Menu options for Human vs Human or Human vs AI games.
- Quick-start tutorial plus an in-depth "Complete Go Guide" covering strategy and rules.
- Optional integration with top-tier AI engines (KataGo/Leela Zero) through GTP.
- Captured stone tracker and last-move highlight.
- Runs on Windows, macOS, Linux (Python + Tkinter).
- No install needed – just download and double-click!

## How to Download & Run

1. **Install Python** (if not already installed):
   - [Download Python here](https://www.python.org/downloads/) (choose the latest version for your OS).
   - Make sure to check "Add Python to PATH" during installation.

2. **Download the game**:
   - Save `go_game.py` to your computer (right-click “Raw” → Save As).

3. **Run the game**:
   - Double-click `go_game.py`  
     Or  
   - Open a terminal/command prompt in the folder and enter:
     ```
     python go_game.py
     ```

## Tutorial

Click "Quick Tutorial" in the start menu for a bite-sized primer or open "Complete Go Guide" for a comprehensive rules and strategy walkthrough.

## Strong AI Integration (Optional)

The default AI plays simple filler moves. To connect a professional-strength engine (such as [KataGo](https://github.com/lightvector/KataGo) or [Leela Zero](https://github.com/leela-zero/leela-zero)):

1. Install the engine of your choice and download its neural network weights.
2. Copy `engine_config.example.json` to `engine_config.json` and edit the `command` to launch your engine in **GTP mode**. For KataGo this usually looks like:
   ```json
   {
     "command": "katago gtp -model /path/to/model.bin.gz -config /path/to/gtp.cfg",
     "startup_commands": [
       "time_settings 0 30 1"
     ]
   }
   ```
3. Make sure the paths in the command exist on your machine.
4. Start a Human vs AI game from the menu. The game will automatically switch to the strong engine when the configuration is valid. If anything fails, it safely falls back to the built-in beginner AI.

> **Tip:** Use smaller boards (9x9/13x13) for quick practice and life-and-death training against the AI.

## Notes

- This is a beginner-friendly version. Automatic scoring beyond captures/territory counting is not implemented.
- External AI engines are optional and must be installed separately.

## License

MIT License