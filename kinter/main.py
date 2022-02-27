from source.framework import Framework


def main():
    framework = Framework()
    framework.mainloop()


if __name__ == "__main__":
    main()


# FIXME:
#  Snake can bite its head after turning very quickly
#  Bonus timers are still counting down while the game is paused

# TODO:
#  Fade background when menus are visible
#  Settings implementation (speed slider, walls switch)
#  High score system implementation (input field widget)
#  Different bonus items with effects on snake/gameplay
#  -----------------------------------------------------
#  Light/Dark theme
#  Intro, Outro
