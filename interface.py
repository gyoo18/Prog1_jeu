#exemple de ui possible

import os
import time


def clearScreen():
    os.system("cls" if os.name == 'nt' else CLEAR)

def dysplayUI(game_map):
    clearScreen()

    header = "=" * 50
    header2 = "inserez titre".center(50)
    header3 = "=" * 50

    print(header)
    print(header2)
    print(header3)




    footer = "=" * 50
    controls = "w (up) s (down) a (left) d (right) q (quit)"
    footer_end = "=" * 50

    print(footer)
    print(controls)
    print(footer_end)


def main():
    width, eight = 20, 10

    game_map = [["." for _ in range(width)] for _ in range(eight)]

    while True:
        dysplayUI(game_map)
        break

if __name__ == "__main__":
    main()

