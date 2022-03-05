from kinter.source.engine.framework import Framework


def main():
    framework = Framework()
    framework.mainloop()


if __name__ == "__main__":
    main()


# FIXME: Window disappears when losing focus

# TODO:
#  - [ BASIC ] -------------------------------------------------
#  Statistics interface
#  Key config implementation (buttons with changing text)
#  Input field widget implementation
#  High score system implementation
#  Leaderboard implementation
#  Graphics wrapper implementation
#  Light/Dark theme
#  - [ GAMEPLAY ] ----------------------------------------------
#  Multiple levels with increasing speed
#  Different bonus items on higher levels (moving bonus, debuff)
#  Enemy snake event on higher levels
#  Intro, Outro
#  - [ PLAYERS ] -----------------------------------------------
#  Profiles and login screen
#  Personal settings
#  Snake customization
#  Personal records
