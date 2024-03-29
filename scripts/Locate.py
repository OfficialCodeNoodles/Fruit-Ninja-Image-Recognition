import math
import numpy as np
import cv2
import time
from operator import add, sub

from Window import *

screenshot = None
screenshotData = None
screenshotSize = None

def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))
def pointify(x1: float, y1: float, x2: float, y2: float, pointCount: int = 10) -> list:
    points = []
    for pointIndex in range(pointCount):
        ratio = pointIndex / pointCount
        points.append(( x1 + (x2 - x1) * ratio, y1 + (y2 - y1) * ratio))
    return points
def sampleColor(region: tuple, samplingPoints: int = 9) -> list:
    getPixelColor = lambda x, y: screenshotData[y][x]
    dimensionalSamplingPoints = samplingPoints**0.5
    left, upper, right, lower = region
    yDelta, xDelta = lower - upper, right - left
    yStep, xStep = math.ceil(yDelta / dimensionalSamplingPoints),\
        math.ceil(xDelta / dimensionalSamplingPoints) 
    colorComponentSum = [ 0, 0, 0 ]
    sampledPoints = 0

    for y in range(upper, lower, yStep):
        for x in range(left, right, xStep):
            pixelColor = getPixelColor(x, y)
            # Add the sum of the sampled pixels components to the combined color
            colorComponentSum = list(map(add, colorComponentSum, pixelColor))
            sampledPoints += 1

    # Return each component divided by the number of points sampled
    return [ componentSum / sampledPoints for componentSum in colorComponentSum ]

def locateObjects(xSamplingPoints = 50, ySamplingPoints = 50) -> list | list:
    global screenshot, screenshotData, screenshotSize

    # Initialize sampling constants
    objectColors = ( 
        # Watermelon & GA   Mango             Apple           Kiwi              Bananna & Lemon
        ( 160, 190, 15 ), ( 255, 215, 50 ), ( 160, 10, 0 ), ( 130, 100, 15 ), ( 225, 220, 30 ), 
        # Coconut & PA      Orange           Peach             Pink Fruit       Bomb
        ( 170, 100, 20 ), ( 230, 130, 0 ), ( 225, 100, 20 ), ( 210, 70, 60 ), ( 40, 30, 30 )
    )
    objectColorDeltaShifts = ( -3, -3, 0, 3, 2, 2, 0, 0, 0, -5 ) # Adjusts detection tolerances
    maxObjectColorDelta = 20 # The default max difference for color sample to be conidered a fruit
    minContinousObjectDistance = scaleComponent(150.0) # Min distance between similiar objects
    samplingSize = int(scaleComponent(60.0)) # Distance for each color sample (in pixels)

    # Take screenshot and update screenshot variables
    screenshot = getGameScreenshot()
    screenshotSize = screenshot.size
    screenshotData = np.array(screenshot) 
    originalScreenshotData = screenshotData.copy() if Properties.recordVideo else None
    modifiedScreenshotData = screenshotData.copy() if Properties.recordVideo else None
    screenshotData = cv2.cvtColor(screenshotData, cv2.COLOR_BGR2RGB)
    
    # Initialize point distribution variables
    xConstrain = lambda x: min(max(x, 0), screenshotSize[0])
    yConstrain = lambda y: min(max(y, 0), screenshotSize[1])
    left, upper, right, lower = 0, 0, screenshot.size[0], screenshot.size[1]
    yDelta, xDelta = lower - upper, right - left
    yStep, xStep = math.ceil(yDelta / ySamplingPoints), math.ceil(xDelta / xSamplingPoints)

    fruits = []
    bombs = []

    # Iterate through each sampling point position
    for y in range(upper, lower, yStep):
        for x in range(left, right, xStep):
            # Determine region to sample color from
            region = [
                xConstrain(x - samplingSize // 2), yConstrain(y - samplingSize // 2), 
                xConstrain(x + samplingSize // 2), yConstrain(y + samplingSize // 2)
            ]
            regionalColor = sampleColor(region)

            # Iterate through each object to see if it matches the samples color
            for i, objectColor in enumerate(objectColors):
                isFruit = i < len(objectColors) - 1 
                objectColorDelta = sum(list(map(abs, list(map(sub, objectColor, regionalColor)))))
                objectColorDelta += objectColorDeltaShifts[i]
                
                if objectColorDelta <= maxObjectColorDelta:
                    objects = fruits if isFruit else bombs
                    appendObject = True
                    
                    # Check if other similiar objects are close by
                    for object in objects:
                        if object[3] == objectColor:
                            objectObjectDistance = distance(*object[:2], x, y)
                        
                            if objectObjectDistance < minContinousObjectDistance:
                                # Remove nearby object if its color delta is greater
                                if object[4] < objectColorDelta:
                                    objects.remove(object)
                                else:
                                    appendObject = False
                                break
                    
                    if appendObject:
                        objects.append(( x, y, regionalColor, objectColor, objectColorDelta ))
                    break
            
            # Render sampling points if required
            if Properties.recordVideo and Properties.recordSamplingPoints:
                sampleBoxSize = 2
                cv2.rectangle(
                    modifiedScreenshotData, pt1=(x, y),
                    pt2=(x + sampleBoxSize, y + sampleBoxSize), 
                    color=(100, 100, 100), thickness=-1
                )

    # Sort fruits so that the closest matches are in the front
    fruits = sorted(fruits, key=lambda object: object[4]\
        + abs(object[1] - Properties.gameScreenRegion["height"] * 0.5) * scaleComponent(0.02))

    # Update discard points
    discardedCoordsCopy = Properties.discardedCoords.copy()
    currentTime = time.time()

    for discardedCoord, expirationTime in discardedCoordsCopy.items():
        if expirationTime <= currentTime:
            del Properties.discardedCoords[discardedCoord]

    fruitsCopy = fruits.copy()
    maxDiscardDistance = scaleComponent(150.0)

    for bomb in bombs:
        Properties.discardedCoords[bomb[:2]] = time.time() + 1.5

    # Remove fruits that're within any discard points
    for fruit in fruitsCopy:
        for discardedCoord in Properties.discardedCoords.keys():
            fruitDiscardedCoordDistance = distance(*fruit[:2], *discardedCoord[:2])

            if fruitDiscardedCoordDistance <= maxDiscardDistance:
                fruits.remove(fruit)
                break

    # Render screenshot data if needed
    if Properties.recordVideo:
        Properties.baseVideo.write(originalScreenshotData.astype("uint8"))

        objectBoxSize = scaleComponent(200.0)
        color = (255, 255, 255)
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = scaleComponent(0.75)
        fontThickness = int(scaleComponent(2.0))
        lineType = cv2.LINE_AA

        for i, object in enumerate(fruits + bombs):
            isFruit = i < len(fruits)
            boxCorner = (
                int(object[0] - objectBoxSize * 0.5), int(object[1] - objectBoxSize * 0.5)
            )
            accuracy = max(math.sqrt(
                (maxObjectColorDelta - object[4]) / maxObjectColorDelta
            ) * 100.0, 1.0)

            # Render outline box, and title
            cv2.rectangle(
                modifiedScreenshotData, pt1=boxCorner,
                pt2=(int(boxCorner[0] + objectBoxSize), int(boxCorner[1] + objectBoxSize)), 
                color=color, thickness=int(scaleComponent(8.0))
            )
            cv2.putText(
                modifiedScreenshotData, f"{"Fruit" if isFruit else "Bomb"} {accuracy:.2f}%", 
                org=(boxCorner[0], int(boxCorner[1] - scaleComponent(20.0))),
                fontFace=font, fontScale=fontScale, color=color, thickness=fontThickness, 
                lineType=lineType
            )

            sampleBoxCorner = (
                int(boxCorner[0] + scaleComponent(167.0)), 
                int(boxCorner[1] - scaleComponent(43.0))
            )
            sampleBoxSize = scaleComponent(30.0)
            objectColor = object[2][::-1]

            # Render color sample box
            cv2.rectangle(
                modifiedScreenshotData, pt1=sampleBoxCorner,
                pt2=(int(sampleBoxCorner[0] + sampleBoxSize), int(sampleBoxCorner[1] + sampleBoxSize)), 
                color=objectColor, thickness=-1
            )

        Properties.modifiedVideo.write(modifiedScreenshotData.astype("uint8"))

    return fruits, bombs