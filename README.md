# Labyrinth Game with Joystick and Controller Control

This project is a labyrinth game implemented in Python using Pygame, supporting both joystick and PS4 controller input. It runs on a Raspberry Pi, where the player moves through the maze to collect letters and complete the word "WEIDMÜLLER" within a time limit of 15 minutes.

## Requirements

- Raspberry Pi with GPIO support
- Python 3
- Pygame library
- RPi.GPIO library (for joystick support)
- PS4 controller support (`pyPS4Controller` library)

## Setup

1. **Install Python Libraries**
   
   Make sure you have Python 3 installed, along with the required libraries:
   
   ```sh
   sudo apt-get install python3-pygame
   sudo pip3 install RPi.GPIO pyPS4Controller
   ```

2. **Wiring the Joystick**
   
   If using the joystick, connect it to the Raspberry Pi using the following GPIO pins:
   - **UP_PIN**: GPIO 17
   - **DOWN_PIN**: GPIO 18
   - **LEFT_PIN**: GPIO 27
   - **RIGHT_PIN**: GPIO 22

3. **Connect the PS4 Controller**
   
   Connect a PS4 controller via Bluetooth or USB. To connect via Bluetooth, put the controller in pairing mode and connect using the Raspberry Pi's Bluetooth settings.

4. **Run the Game**
   
   To run the game, execute the following command:
   
   ```sh
   python3 main.py
   ```

## How to Play

- The objective of the game is to collect all the letters scattered across the maze to complete the word "WEIDMÜLLER".
- Use the joystick or PS4 controller to move your character through the maze. You can move **UP**, **DOWN**, **LEFT**, or **RIGHT**.
- You have 15 minutes to complete the game.
- Collect power-ups such as **boost** and **shield** to enhance your gameplay.

## Features

- **Random Maze Generation**: The maze is randomly generated each time you play, ensuring a unique experience.
- **Joystick and Controller Control**: Control the player character using a physical joystick connected to the Raspberry Pi or a PS4 controller.
- **Dynamic Camera**: The view follows the player to show only a portion of the maze, adding an element of exploration.
- **Power-Ups with Visual Feedback**: Collect boost and shield power-ups, which are visually represented to enhance the gaming experience.

## File Information

- `main.py`: This is the main file that contains all the game logic, maze generation, and GPIO pin setup.

## Troubleshooting

- **Pygame Errors**: Make sure you have installed Pygame correctly. You can install it via `sudo apt-get install python3-pygame`.
- **Joystick Not Responding**: Double-check the wiring and GPIO pin assignments to ensure everything is connected properly.
- **PS4 Controller Issues**: Ensure that the controller is properly paired and the `pyPS4Controller` library is installed.
- **Permission Issues**: You may need to run the script with `sudo` to access GPIO pins.

## License

This project is licensed under the MIT License.

