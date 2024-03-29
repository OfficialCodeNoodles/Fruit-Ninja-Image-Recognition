import mss

import Properties

def gameToScreenCoord(x: float, y: float) -> float | float:
    return x + Properties.gameScreenRegion["left"], y + Properties.gameScreenRegion["top"]
def screenToGameCoord(x: float, y: float) -> float | float:
    return x - Properties.gameScreenRegion["left"], y - Properties.gameScreenRegion["top"]
def scaleComponent(val: float) -> float:
    return val * Properties.gameScreenScale

def getGameScreenshot():
    with mss.mss() as sct:
        screenshot = sct.grab(Properties.gameScreenRegion)
        return screenshot