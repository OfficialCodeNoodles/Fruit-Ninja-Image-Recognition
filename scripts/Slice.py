import pyautogui

from Locate import *

def slice(x1: float, y1: float, x2: float, y2: float):
    # Transform coords to work with mouse
    x1, y1 = gameToScreenCoord(x1, y1)
    x2, y2 = gameToScreenCoord(x2, y2)

    pyautogui.moveTo(x1, y1, _pause=False)
    pyautogui.mouseDown(_pause=False)
    pyautogui.sleep(0.01)
    pyautogui.moveTo(x2, y2, 0.04, _pause=False)
    pyautogui.sleep(0.03)
    pyautogui.mouseUp(_pause=False)
    pyautogui.sleep(0.01)
def sliceFruits(fruits: list, bombs: list):
    if len(fruits) > 0:
        # Minimum distance required between a fruit and the bombs that can be sliced
        minFruitBombDistance = scaleComponent(400.0)
        fruitIndex = 0

        # Search for a safe fruit to slice
        while True:
            selectedFruit = fruits[fruitIndex]
            safeFruitFound = True

            # Check if the selected fruit is too close to any bombs
            for bomb in bombs:
                fruitBombDistance = distance(*selectedFruit[:2], *bomb[:2])

                if fruitBombDistance < minFruitBombDistance:
                    fruitIndex += 1
                    if fruitIndex >= len(fruits):
                        return
                    safeFruitFound = False
                    break

            if safeFruitFound:
                break

        sliceLength = 250.0
        sliceStart = ( selectedFruit[0], selectedFruit[1] + sliceLength * 0.5 )
        sliceEnd = ( selectedFruit[0], selectedFruit[1] - sliceLength * 0.5 )

        slicingArgs = (*sliceStart, *sliceEnd)
        slice(*slicingArgs)
        points = pointify(*slicingArgs)

        if selectedFruit[3] != ( 210, 70, 60 ):
            # Discard points along the slice
            for point in points:
                Properties.discardedCoords[point] = time.time() + 1.0
        else:
            slice(*slicingArgs)
