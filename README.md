# Jamjam - Emoji Match-3 Game

A Pygame-based Match->3 puzzle game (similar to Candy Crush) featuring smooth animations and cascading tile mechanics.

## Features

- **6x6 Grid Gameplay**: Classic match-3 mechanics with horizontal and vertical matching
- **Smooth Animations**: 
  - Tile swap animations when you swap adjacent tiles
  - Falling tile animations as pieces drop into place
  - Shrinking animations when tiles are cleared
- **Cascading Matches**: Automatic detection and clearing of cascading matches
- **Score Tracking**: Points awarded for matched tiles
- **Emoji Tiles**: Colorful emoji graphics for game tiles

## Requirements

- Python 3.x
- Pygame

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install pygame
   ```

## Running the Game

```bash
python ai_version.py
```

## How to Play

1. **Select a tile** by clicking on it
2. **Click an adjacent tile** to swap positions
3. **Match 3+ tiles** in a row (horizontally or vertically) to clear them
4. **Earn points** - each cleared tile is worth 10 points
5. **Chain matches** - cascading matches occur automatically after tiles fall

## Game Assets

The game requires the following image files in an `img/` directory:
- `board.png` - Game board background
- `emoji1.png` through `emoji5.png`

## Game Settings

Key constants in `ai-human_version.py`:
- `GRID = 6` - Board size (6x6)
- `TILE = 80` - Tile size in pixels
- `ANIM_DURATION = 600` - Swap animation duration (ms)
- `FALL_DURATION = 900` - Fall animation duration (ms)
- `SHRINK_DURATION = 150` - Shrink animation duration (ms)

## Course

ITEC1401
