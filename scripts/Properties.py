from os.path import exists
import json

discardedCoords = {}
gameScreenRegion = { "left": 400, "top": 0, "width": 1760, "height": 1440 }
gameScreenScale = 1.0
recordVideo = False
recordSamplingPoints = False
baseVideo = None
modifiedVideo = None

def load(filename: str = "properties.json"):
    if not exists(filename):
        save()
        return
    
    global gameScreenRegion, gameScreenScale, recordVideo, recordSamplingPoints
    
    # I know it's messy
    with open(filename, 'r') as propertyFile:
        attributes = json.load(propertyFile)
        gameScreenRegion["left"] = attributes["gameScreenLeft"]
        gameScreenRegion["top"] = attributes["gameScreenTop"]
        gameScreenRegion["width"] = attributes["gameScreenWidth"]
        gameScreenRegion["height"] = attributes["gameScreenHeight"]
        gameScreenScale = attributes["gameScreenScale"]
        recordVideo = attributes["recordVideo"]
        recordSamplingPoints = attributes["recordSamplingPoints"]
def save(filename: str = "properties.json"):
    # and unconventional
    with open(filename, 'w') as propertyFile:
        attributes = {
            "gameScreenLeft": gameScreenRegion["left"],
            "gameScreenTop": gameScreenRegion["top"],
            "gameScreenWidth": gameScreenRegion["width"],
            "gameScreenHeight": gameScreenRegion["height"],
            "gameScreenScale": gameScreenScale,
            "recordVideo": recordVideo,
            "recordSamplingPoints": recordSamplingPoints
        }
        json.dump(attributes, propertyFile, indent=4)