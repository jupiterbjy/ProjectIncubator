import trio

import MainApp

if __name__ == '__main__':
    trio.run(MainApp.MainApp().trio_driver)
