import time
import pyautogui as pag
import pyperclip

YOUTUBE_URL = "https://www.youtube.com/watch?v=0A4_eiJp0SI"

def wait(sec=1):
    time.sleep(sec)

def open_chrome_guest():
    # Open Run dialog
    pag.hotkey("win", "r")
    wait(0.5)

    # Open Chrome in Guest mode
    pag.typewrite('chrome --guest', interval=0.03)
    pag.press("enter")
    wait(3)

def open_youtube(url):
    pag.hotkey("ctrl", "l")   # Address bar
    wait(0.2)

    pyperclip.copy(url)
    pag.hotkey("ctrl", "v")
    wait(0.2)

    pag.press("enter")
    wait(5)

def play_video():
    # Play
    pag.press("k")
    wait(1)

    # Fullscreen
    pag.press("f")
    wait(1)

def main():
    pag.FAILSAFE = True
    print("Starting in 2 seconds (move mouse to top-left to abort)")
    wait(2)

    open_chrome_guest()
    open_youtube(YOUTUBE_URL)
    play_video()

    print("✅ Video is playing in Guest mode")

if __name__ == "__main__":
    main()
