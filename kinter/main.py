from kinter.source.engine.framework import Framework


def main():
    framework = Framework()
    framework.mainloop()


if __name__ == "__main__":
    main()


# TODO:
#  - [ BASIC ] -------------------------------------------------
#  Statistics interface
#  High score system implementation (leaderboard, input field widget)
#  Key config implementation (buttons with changing text)
#  Light/Dark theme
#  - [ GAMEPLAY ] ----------------------------------------------
#  Multiple levels with increasing speed
#  Different bonus items on higher levels (moving bonus, debuff)
#  Enemy snake event on higher levels
#  Intro, Outro
#  - [ PLAYERS ] -----------------------------------------------
#  Profiles and login
#  Personal settings
#  Snake customization
#  Personal record
