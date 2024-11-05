# Labyrinth Game with Joystick Control

This project is a labyrinth game implemented in Python using Pygame and a joystick connected to a Raspberry Pi. The player moves through the maze to collect letters and complete the word "WEITMÜLLER" within a time limit of 10 minutes.

## Requirements

- Raspberry Pi with GPIO support
- Python 3
- Pygame library
- RPi.GPIO library
- Arduino joystick module

## Setup

1. **Install Python Libraries**
   
   Make sure you have Python 3 installed, along with the required libraries:
   
   ```sh
   sudo apt-get install python3-pygame
   sudo pip3 install RPi.GPIO
   ```

2. **Wiring the Joystick**
   
   Connect the joystick to the Raspberry Pi using the following GPIO pins:
   - **UP_PIN**: GPIO 17
   - **DOWN_PIN**: GPIO 18
   - **LEFT_PIN**: GPIO 27
   - **RIGHT_PIN**: GPIO 22

3. **Run the Game**
   
   To run the game, execute the following command:
   
   ```sh
   python3 main.py
   ```

## How to Play

- The objective of the game is to collect all the letters scattered across the maze to complete the word "WEITMÜLLER".
- Use the joystick to move your character through the maze. You can move **UP**, **DOWN**, **LEFT**, or **RIGHT**.
- You have 10 minutes to complete the game.

## Features

- **Random Maze Generation**: The maze is randomly generated each time you play, ensuring a unique experience.
- **Joystick Control**: Control the player character using a physical joystick connected to the Raspberry Pi.
- **Dynamic Camera**: The view follows the player to show only a portion of the maze, adding an element of exploration.

## File Information

- `main.py`: This is the main file that contains all the game logic, maze generation, and GPIO pin setup.

## Troubleshooting

- **Pygame Errors**: Make sure you have installed Pygame correctly. You can install it via `sudo apt-get install python3-pygame`.
- **Joystick Not Responding**: Double-check the wiring and GPIO pin assignments to ensure everything is connected properly.
- **Permission Issues**: You may need to run the script with `sudo` to access GPIO pins.

## License

This project is licensed under the MIT License.

