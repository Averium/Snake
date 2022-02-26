from source.framework import Framework


def main():
    framework = Framework()
    framework.mainloop()


if __name__ == "__main__":
    main()


# TODO:
#  Exit button in corner
#  State machine implementation (non periodic timer implementation)
#  Basic interface implementation
#  Event handler update (use key codes instead of names)
#  Input queue for turn
#  Animations in non-game states
#  Settings implementation
#  High score system implementation (input field widget)
#  Light/Dark theme
