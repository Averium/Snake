from source.framework import Framework


def main():
    framework = Framework()
    framework.mainloop()


if __name__ == "__main__":
    main()


# FIXME:
#  Snake can bite its head after turning very quickly

# TODO:
#  - [ BASIC ] ----------------------------------------------
#  Interface update with more labels
#  Info panel implementation (score label, speed, statistics)
#  Settings implementation (speed slider, walls switch)
#  Moving bonus
#  High score system implementation (input field widget)
#  Light/Dark theme
#  - [ GAMEPLAY ] -------------------------------------------
#  Multiple levels with increasing speed
#  Different bonus items on higher levels
#  Enemy snake event on higher levels
#  Intro, Outro
#  - [ PLAYERS ] --------------------------------------------
#  Profiles and login
#  Personal settings
#  Snake customization
