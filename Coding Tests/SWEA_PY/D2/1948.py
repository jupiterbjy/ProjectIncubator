from datetime import datetime


for test_no in range(1, int(input()) + 1):
    m1, d1, m2, d2 = map(int, input().split())
    print(f"#{test_no} {(datetime(2023, m2, d2) - datetime(2023, m1, d1)).days + 1}")
