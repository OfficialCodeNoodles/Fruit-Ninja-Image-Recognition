import keyboard

from Slice import *

appTitle = "Fruit Ninja Image Recognition"
appRunning = True

def init():
    global appRunning

    if pyautogui.confirm(
        text="A barely functional Fruit Ninja AI - CodeNoodles (2024)\n\n"
            "  Keybinds:\n    1. Escape - Exit program\n    2. P - Pause program",
        title=appTitle,
        buttons=("Begin", "Cancel")
    ) != "Begin":
        appRunning = False
        return

    pyautogui.FAILSAFE = False
    Properties.load()
    pyautogui.sleep(2.0)

    if Properties.recordVideo:
        def getVideoFilename(base: bool) -> str:
            videoIndex = 1
            while True:
                videoFilename = f"capture/{"Base" if base else "Modified"}{videoIndex}.mp4"
                if not Properties.exists(videoFilename):
                    return videoFilename
                videoIndex += 1

        # Initialize codec. Note: You may need a different codec on your computer
        codec = cv2.VideoWriter_fourcc(*"H264")
        framerate = 15.0
        resolution = ( Properties.gameScreenRegion["width"], Properties.gameScreenRegion["height"] )

        # Intitialize video writers
        Properties.baseVideo = cv2.VideoWriter(
            getVideoFilename(True), codec, framerate, resolution
        )
        Properties.modifiedVideo = cv2.VideoWriter(
            getVideoFilename(False), codec, framerate, resolution
        )
def update():
    # Continously run application until escape is pressed
    while not keyboard.is_pressed("escape") and appRunning:
        # Pause application when p key is pressed
        if keyboard.is_pressed('p'):
            if pyautogui.confirm(
                text="Application paused...",
                title=appTitle,
                buttons=("Unpause", "Exit")
            ) != "Unpause":
                break

        fruits, bombs = locateObjects()
        sliceFruits(fruits, bombs)
def close():
    if Properties.recordVideo and appRunning:
        # Cleanup video writers
        Properties.baseVideo.release()
        Properties.modifiedVideo.release()

if __name__ == "__main__":
    init()
    update()
    close()