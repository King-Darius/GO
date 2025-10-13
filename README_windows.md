# Go Game (Windows EXE)

This folder contains a simple Go game you can play—no installation or coding needed!

## How to Run

1. **Double-click** `go_game.exe` in the `dist` folder.
2. **Play!**
   - Choose Human vs Human or Human vs AI on 9x9, 13x13, or 19x19 boards.
   - Use "Quick Tutorial" for the basics or "Complete Go Guide" for a deep dive into rules and strategy.

## What if it doesn't work?

- If you see errors, right-click `go_game.exe` and choose "Run as administrator".
- Some antivirus programs might warn about new .exe files—this is normal for homemade apps.
- If it doesn't open, make sure you downloaded all files and your Windows is up to date.

## Want to see the source code?

Check out `go_game.py`!

## Want a super-strong AI opponent?

1. Install a Go engine that speaks **GTP** (for example [KataGo](https://github.com/lightvector/KataGo/releases) for Windows).
2. Copy `engine_config.example.json` to `engine_config.json` and edit the command so it launches your engine and points to the neural network/model files.
3. Place the config file next to `go_game.py` (the same folder as the executable if you bundle it).
4. Start a Human vs AI game—the app will connect to the engine automatically. If anything goes wrong, it falls back to the built-in beginner AI.

> **Tip:** Playing 9x9 against KataGo is an excellent way to sharpen reading skills quickly.
