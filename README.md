# Fruit Ninja Image Recognition
This is a Python program that can play the popular game **Fruit Ninja** by using image recognition.

# How does it work?
The program works by taking a screenshot of the game, and sampling a bunch of points from the screenshot to try and locate fruits and bombs. Then from there, some transformations are done to the data to try and remove counterproductive things (like duplicate fruits in a small region), and then the program slices the fruits that are in safe locations (to avoid bombs)

# Dependencies

- Pyautogui
- Pillow
- Opencv-python
- Numpy
- Mss
- Keyboard

# Notes

- Make sure to update `properties.json` to match the dimensions of the game and window to yours, as well as the scale
- You can also disable the video feature in `properties.json` if the program isn't able to keep up
