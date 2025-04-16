# Weidmüller Escape Room Labyrinth

A 2D maze game where you need to collect letters while avoiding bosses. Use a PS4 controller or WASD keys to navigate through the maze.

## Features
- Three difficulty levels (Easy, Medium, Hard)
- PS4 controller support
- Intelligent boss AI with pathfinding
- Dynamic maze navigation
- Time-based challenge
- Letter collection mechanic

## Difficulty Levels
- Easy:
  - Time Limit: 10 minutes
  - Slower boss movement
  - All letters to collect: WEIDMULLER
- Medium:
  - Time Limit: 7 minutes
  - Moderate boss movement
  - All letters to collect: WEIDMULLER
- Hard:
  - Time Limit: 5 minutes
  - Fast boss movement
  - All letters to collect: WEIDMULLER

## Controls
### PS4 Controller:
- Left Stick/D-pad: Move character
- X Button: Interact
- Menu Navigation: D-pad/Left Stick + X Button

### Keyboard (Fallback):
- W: Move up
- A: Move left
- S: Move down
- D: Move right
- Menu Navigation: Arrow Keys + Enter

## Gameplay
1. Select difficulty level at start
2. Navigate through the maze to collect all hidden letters
3. Avoid the four boss enemies that chase you
4. Complete the game within the time limit
5. Answer the final question correctly to win
6. Getting caught by a boss results in game over

## Installation
1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the game:
```bash
python main.py
```
