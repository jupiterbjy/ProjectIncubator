trans = {"MON": 6, "TUE": 5, "WED": 4, "THU": 3, "FRI": 2, "SAT": 1, "SUN": 7}
for test_no in range(1, int(input()) + 1):
    print(f"#{test_no}", trans[input()])
