# quite a terrible problem, acceleration in 0sec??

for test_no in range(1, int(input()) + 1):
    dist = 0
    speed = 0

    for _ in range(int(input())):
        cmd = input()

        if cmd[0] == "1":
            speed += int(cmd[2:])

        elif cmd[0] == "2":
            tgt = int(cmd[2:])
            speed = 0 if speed < tgt else speed - tgt

        dist += speed

    print(f"#{test_no} {dist}")
