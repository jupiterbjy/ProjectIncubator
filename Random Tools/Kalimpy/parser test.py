from parser.parser import tune, TabLine, tab_parser
import time


if __name__ == '__main__':
    import winsound

    line = r"1'  1'2' 2'  1' 1'3'4'3'  1'  1'2' 2'  1' 1' 7 1' /"
    tune("C4 D4 E4 F4 G4 A4 B4 C5 D5 E5 F5 G5 A5 B5 C6 D6 E6".split())

    parsed = TabLine(tab_parser(line))
    duration = 200

    for tab in parsed:
        print(tab)
        if tab.frequency:
            winsound.Beep(int(tab.frequency), duration)
        else:
            time.sleep(duration / 1000)
