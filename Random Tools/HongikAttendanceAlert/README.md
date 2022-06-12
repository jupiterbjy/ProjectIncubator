## Introduction

10분 쉬다오래서 쉬다오니 1분짜리 시간제한 출석코드를 도중에 던져놔서 겁내 터졌는데, 기분이 참 안좋아요. 쉬래놓고 1분을 걸다니.

그래서 시험삼아 만들어봤습니다. 10~15초 주기로 체크하여 새 출석코드 체크가 있으면 경고음을 3번 울립니다.
(터미널에서 ctrl+G 지원할 경우)

학교에서 이걸 금지할진 모르겠지만.

## Requirements

- module
    - python 3.8+
    - selenium
    - Firefox webdriver

## Usage

받은 폴더 밖에서 python + 폴더명 입력

```commandline
python3 HongikAttendanceAlert
```

기다리다 파이어폭스에 로그인창 뜨면 로그인 진행, 이후 냅두면 됩니다.
